from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


url = "http://jandan.net/ooxx/page-"
num = 2259
for i in range(997, 1058):
    try:
        r = urlopen(url + str(i)).read().decode()
        b = BeautifulSoup(r)
        imgs = b.select('li p img')
        for img in imgs:
            num += 1
            print(i, num, img['src'])

            data = {
                'name': str(num) + '.jpg',
                'url': img['src'],
            }
            print(data)
    except HTTPError as e:
        pass