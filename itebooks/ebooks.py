from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


class ItEBooks():
    url = 'http://it-ebooks.info/book/'

    def __init__(self, start=1, end=3138):
        self.start = start
        self.end = end

    def fork(self):
        for i in range(self.start, self.end):
            try:
                response = urlopen(self.url + str(i))
                result = BeautifulSoup(response.read())
                title = result.title.string.strip(' - - Free Download eBook - pdf')
                print(i, title)
            except HTTPError as e:
                print(i, e)


if __name__ == '__main__':
    books = ItEBooks(1, 50)
    books.fork()
