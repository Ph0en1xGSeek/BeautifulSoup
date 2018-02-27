import requests
from bs4 import BeautifulSoup
import json
import time
import numpy as np

#抓取的网页地址模版，所有分页的目录
listURL = 'http://www.cnair.com/city/Japan/index{}.htm'
lists = [listURL.format('')]
# lists = []
for i in range(1, 45):
    lists.append(listURL.format(str(i)))
#打开一个文件用于append抓到的信息
f = open("gpsmap.json", "a")


# print(lists)

dic = {}

for item in lists:
    #使用Requests请求页面
    res = requests.get(item)
    # print(res.text)
    #解析html文本
    soup = BeautifulSoup(res.text, 'html.parser')
    #选取出页面中mainNewsTitle类下的<a>标签
    urls = soup.select('.mainNewsTitle a')
    # print(urls)
    for u in urls:
        # print(u['href'])
        #取出每个<a>标签下的href属性并请求该页面
        tmpres = requests.get(u['href'])
        #解析需要使用utf8编码
        tmpres.encoding = 'utf_8'
        tmpsoup = BeautifulSoup(tmpres.text, 'html.parser')
        text = tmpsoup.select('.NewsContent')
        textarr = str(text[0]).split('<br/>')
        #取出城市名称
        name = textarr[1].split(' : ')[1]
        #取出经度
        lng = textarr[6].split(' : ')[1]
        #取出纬度
        lat = textarr[5].split(' : ')[1]

        #将经纬度统一换算成‘度’的形式
        lngarr = lng.split('°')
        fen = float(lngarr[1].split('\'')[0])
        du  = float(lngarr[0])
        lng = du + (fen/60)

        latarr = lat.split('°')
        fen = float(latarr[1].split('\'')[0])
        du  = float(latarr[0])
        lat = du + (fen/60)

        #存下刚刚抓取的信息
        tmpdic = {}
        tmpdic['lng'] = lng
        tmpdic['lat'] = lat
        dic[name] = tmpdic
        print('{} {} {}'.format(name, lng, lat), file=f)
        print('{} : {}: {}: {}'.format(item, name, lng, lat))
        #停顿1秒
        time.sleep(1)
    time.sleep(10)
#存储抓取的结构化信息
jsonStr = json.dumps(dic)
f = open("gpsmap.json", "w")
print(jsonStr, file=f)
f.close()