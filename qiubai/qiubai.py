from urllib.request import urlopen, Request, HTTPError
from bs4 import BeautifulSoup


class Quibai():
    url = 'http://www.qiushibaike.com/'

    def __init__(self, start=1, end=20, save=False):
        """
        start 起始页
        end 结束页
        save 是否保存到数据库
        """
        self.start = start
        self.end = end
        self.save = save

    def fork(self, url='8hr/page/'):
        """默认是8小时内容
        fork 不同的内容只需要修改url参数，也可以调用下面的快捷方法
        糗百的页面结构貌似都是相同的，原则上也可以fork history部分，需要判断日期
        """
        url = self.url + url
        for self.start in range(self.end):
            page_url = url + str(self.start)
            r = Request(page_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'})
            try:
                response = urlopen(r)
                result = BeautifulSoup(response.read())
                contents = result.find_all(class_='content')
                for c in contents:
                    if c.string:
                        title = c.string.strip()
                        p = c.parent
                        thumb = p.find(class_='thumb')
                        if thumb:
                            image = thumb.a.img['src']
                        else:
                            image = ''
                        print(title, image)
            except HTTPError:
                pass

    def fork_24hours(self):
        self.fork(url='hot/page/')

    def fork_week(self):
        self.fork(url='week/page/')

    def fork_month(self):
        self.fork(url='month/page/')


if __name__ == '__main__':
    qiubai = Quibai()
    qiubai.fork()
    # qiubai.fork_24hours()
    # qiubai.fork_week()
    # qiubai.fork_month()