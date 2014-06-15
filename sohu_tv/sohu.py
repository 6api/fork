"""搜狐视频爬虫，获取视频信息
采用广度优先策略进行爬取，维护两个队列，一个用于存放待爬取的url地址，一个用于存放待提取信息的视频url地址。
使用MongoDB存储已经爬取得地址，用于比对去重，url存储时进行hash（既存原始地址，又存hash值方便去重时比对）。

为提高性能，对于已经爬取得地址，可以用redis代替MongoDB进行存储?

测试环境 ubuntu 13.10 + python3.3.2

！声明： 爬虫仅用于学习研究，勿用于其他用途

@author imaguowei@gmail.com
@date 2014-03-17

"""
import re
from hashlib import sha1
from threading import Thread
from queue import Queue
from urllib.request import urlopen, Request
from pymongo import MongoClient
from bs4 import BeautifulSoup


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    "Referer": 'http://www.google.com'
}


def get_html(url):
    """根据url获取整个页面
    如果大量抓取，最好添加代理
    """
    #设置User-Agent
    req = Request(url, headers=header)
    response = urlopen(req)
    return response.read()


def counter(name):
    """用于产生自增id
    参考：http://stackoverflow.com/questions/9938418/how-to-create-human-readable-id-in-mongodb
    """
    ret = MongoClient().sohu.counters.find_and_modify(query={'id': name}, update={'$inc': {'next': 1}},
                                                      upsert=True, new=True)
    return ret['next']


class UrlCollector(Thread):
    """广度优先收集url地址
    """
    #需要处理的url规则（加入queue),不符合直接丢弃
    pattern = re.compile(r'http://.*tv.sohu.com')

    #需要提取内容的url规则(加入tv_queue)
    pattern2 = re.compile(r'http://.*tv.sohu.com(/us)?/\d*/n?\d*.shtml')

    def __init__(self, queue, tv_queue, count_queue, video_num, start='http://tv.sohu.com'):
        Thread.__init__(self)
        self.queue = queue
        self.tv_queue = tv_queue
        self.count_queue = count_queue
        self.db = MongoClient().sohu
        self.video_num = video_num

        #当数据库不存在任何链接时加入起始种子url,并加入队列
        if not self.db.url.count():
            self.insert_url(start)
            self.queue.put(start)

    def insert_url(self, url):
        """将url插入数据库"""
        self.db.url.insert({'url': url, 'id': self.hash_url(url)})

    @staticmethod
    def hash_url(url):
        """对 url hash 处理
        """
        return sha1(url.encode()).hexdigest()

    def fetch_urls(self, soup):
        """从页面提取合法链接
        过滤无用链接
        """
        aas = soup.find_all('a')
        #匹配所有 tv.sohu.com 下的url
        for a in aas:
            href = a.get('href', '').split('?')[0]
            if self.pattern.match(href) is not None:
                u_id = self.hash_url(href)
                result = self.db.url.find_one({'id': u_id})
                #可能有并发问题，但是遇到冲突几率很小，可以忽略
                if result:
                    print('链接已存在', href)
                else:
                    print('添加链接', href)
                    self.insert_url(href)
                    self.queue.put(href)

                    if self.pattern2.match(href) is not None:
                        self.tv_queue.put(href)
            else:
                print('无效链接', href)

    def run(self):
        while True:
            print('UrlCollector', self.getName(), self.queue.qsize())
            # tv_queue大于需要抓取的视频数目等待直到Tv将其处理完成，或者count_queue清空，随主线程一同退出
            if self.tv_queue.qsize() > self.video_num:
                print('collector 等待tv处理')
                self.count_queue.join()
            try:
                url = self.queue.get()
                print(self.getName(), url)
                html = get_html(url)
                soup = BeautifulSoup(html)
                self.fetch_urls(soup)
            except Exception as e:
                print(e)
                continue


class Tv(Thread):
    """处理queue_tv队列,提取视频信息
    """
    def __init__(self, tv_queue, count_queue):
        Thread.__init__(self)
        self.tv_queue = tv_queue
        self.count_queue = count_queue
        self.db = MongoClient().sohu

    @staticmethod
    def parse(url):
        """页面解析，提取视频信息
        """
        html = get_html(url)
        soup = BeautifulSoup(html)
        head = soup.head
        data = {}
        metas = head.find_all('meta')
        for n, meta in enumerate(metas):
            if meta.get('name') is None or meta.get('property') is None:
                del metas[n]

            data = {meta.get('name') if meta.get('name') is not None else meta.get('property'): meta['content']
                    for meta in metas}
        return data

    def run(self):
        while self.count_queue.empty() is False:
            try:
                url = self.tv_queue.get()
                data = self.parse(url)
                #自增id
                data['id'] = counter('tv')
                self.db.tv.insert(data)
                self.count_queue.get()
                print('Tv', self.getName(), self.tv_queue.qsize(), self.count_queue.qsize())
                self.count_queue.task_done()
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    #起始种子地址
    start_url = 'http://tv.sohu.com/map/'
    #设置要抓取视频信息的数目
    video_num = 1300

    #获得url队列
    queue = Queue()
    #需要提取视频信息的url队列
    tv_queue = Queue()
    #用于计数的队列
    count_queue = Queue()

    for c in range(video_num):
        count_queue.put(c)

    for i in range(3):
        url_collector = UrlCollector(queue, tv_queue, count_queue, video_num, start_url)
        #随主线程一同结束，下同
        url_collector.daemon = True
        url_collector.start()

    for j in range(5):
        tv = Tv(tv_queue, count_queue)
        tv.daemon = True
        tv.start()

    #阻塞直到计数队列为空
    count_queue.join()
    print('<<<<<<<<<<<<<<<<任务结束>>>>>>>>>>>>>>>>>>>>>>')