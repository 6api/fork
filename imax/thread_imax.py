""" Fork IMax
多线程版本
！！！！！第一次用多线程，待完善

@date 2014-03-1
"""

import threading
from queue import Queue
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


class UrlQueue():
    url = 'http://imax.im/movies/'
    q = Queue()

    def __init__(self, begin=1, end=10):
        self.begin = begin
        self.end = end

        for i in range(self.begin, self.end):
            self.q.put(self.url + str(i))

urlqueue = UrlQueue()
print(urlqueue.q.qsize())


class IMax(threading.Thread):
    error_number = 0

    def run(self):
        while not urlqueue.q.empty():
            movie = dict()
            try:
                response = urlopen(urlqueue.q.get())
                restlt = BeautifulSoup(response.read())

                title = restlt.title.string
                movie['title'] = title.strip('| 高清 BT下载,电驴下载,迅雷下载,在线观看 | IMAX.im')

                movie['db_id'] = restlt.find('div', class_='raters_count').a['href'].strip('http://movie.douban.com/subject/')
                table = restlt.find('table', class_='table table-striped table-condensed')
                trs = table.select('tbody tr')
                download = list()
                for tr in trs:
                    tds = tr.find_all('td')
                    li = dict()
                    for td in tds:
                        if td['class'][0] == 'qu':
                            li['format'] = td.string.strip()
                        elif td['class'][0] == 'size':
                            li['size'] = td.span.string
                        elif td['class'][0] == 'name':
                            li['name'] = td.a.string
                            li['href'] = td.a['href']
                    download.append(li)
                movie['download'] = download
                print(movie)
            except AttributeError as attrerr:
                print(attrerr)
            except HTTPError as e:
                self.error_number += 1
                print(e)


if __name__ == '__main__':
    for j in range(10):
        imax = IMax()
        imax.start()
