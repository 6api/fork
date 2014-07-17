#!/usr/bin/env python
# encoding=utf-8

import re
import html
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


client = MongoClient()
db = client.soyoung
collection = db.item


class SoYoung():
    url = 'http://www.soyoung.com/item'
    @staticmethod
    def convert2num(s):
        return int(s.lstrip('width: ').rstrip('%;')) // 20

    def get_all_item_id(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content)
        for link in soup.find_all('a', id=re.compile(r'c\d+')):
            # print(link['href'])
            d = self.get_page_info(link['href'])
            collection.insert(d)
            print(d)

    def get_page_info(self, page_url):
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content)
        data = {}
        data['item_name'] = soup.find('span', class_='icon').string     #项目名称
        data['slogan'] = soup.find('p', class_='slogan').string         #项目描述

        data['level_attention'] = self.convert2num(soup.find('span', class_='level attention').span['style'])     #关注度
        data['level_safety'] = self.convert2num(soup.find('span', class_='level safety').span['style'])           #安全度
        data['level_complex'] = self.convert2num(soup.find('span', class_='level complex').span['style'])         #复杂度

        item_info = soup.find('div', class_='item_info')
        lis = item_info.ul.find_all('li')

        data['treatment_means'] = lis[3].find('span', class_='c').string.strip()            #治疗手段
        data['effect_continue'] = lis[4].find('span', class_='c').string                    #效果持续
        data['recovery_time'] = lis[5].find('span', class_='c').string                      #恢复时间

        merit_box = soup.find('div', class_='merit_box')
        lis1 = merit_box.find_all('li')

        data['advantage'] = str(lis1[0].find('p', class_='c').get_text())             #优点
        data['disadvantage'] = str(lis1[1].find('p', class_='c').get_text())          #缺点
        data['side_effect'] = str(lis1[2].find('p', class_='c').get_text())          #副作用及风险


        data['item_sub_item'] = str(soup.find('h3').get_text()).lstrip('j')         #

        # first = data['treat_method'] = soup.find('li', class_='first')
        # data['treat_method'] = soup.find('li', class_='first').div
        # data['treat_effect'] = first.next_element
        showitme_box = soup.find('div', class_='showitme_box showitme_box_new')
        lis2 = showitme_box.find_all('li')

        # data['treatment_method'] = str(lis2[0].div.p.get_text()) + lis2[0].div.img['src']                #治疗方法
        # data['treatment_effect'] = str(lis2[1].div.p.get_text() + lis2[1].div.img['src'])                #治疗效果
        data['treatment_method'] = html.escape(str(lis2[0].div))                  #治疗方法
        data['treatment_effect'] = html.escape(str(lis2[1].div))                  #治疗效果
        data['notes'] = str(lis2[2].div.p.get_text())                             #注意事项
        data['fit_people'] = str(lis2[3].div.p.get_text())                        #适合人群
        data['treatment_length'] = lis2[4].div.p.string                           #治疗时长
        data['anesthesia_method'] = lis2[5].div.p.string                          #麻醉方法
        data['hospital_treatment'] = lis2[6].div.p.string                         #住院治疗
        data['line_days'] = lis2[7].div.p.string                                  #拆线天数
        data['treat_num'] = lis2[8].div.p.string                                  #治疗次数
        data['recovery_process'] = lis2[9].div.p.string                           #恢复过程
        # print(lis2)

        return data


if __name__ == '__main__':
    so_young = SoYoung()
    so_young.get_all_item_id()
    # page_info = so_young.get_page_info('http://www.soyoung.com/post/item/item_id/1')
    # print(page_info)