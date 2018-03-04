import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
import re
import pymongo
import os
from config import *
from multiprocessing import Pool
from json.decoder import JSONDecodeError

#连接数据库
client = pymongo.MongoClient(MONGO_URL)
#确定响应的database
db = client[MONGO_DB]

def get_page_index(offset, keyword):
    '''

    :param offset: 页面offset，用于自动append新结果
    :param keyword: 搜索关键字
    :return:
    '''
    #请求的参数
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload':'true',
        'count': '20',
        'cur_tab': 3,
        'from': 'gallery'
    }
    #urlencode可以用来将参数的json串转换为url上的参数
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        #成功200
        if response.status_code == 200:
            # print(response.text)
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None

def parse_page_index(html):
    try:
        #转化为json对象
        data = json.loads(html)
        # print(data)
        #有数据并且又‘data’标签
        if data and 'data' in data.keys():
            for item in data.get('data'):
                if 'article_url' in item.keys():
                    yield item.get('article_url')
    except JSONDecodeError:
        pass


def get_page_detail(url):
    try:
        response = requests.get(url)
        # print(response.text)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错', url)
        return None

def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    #获得页面title
    title = soup.select('title')[0].get_text()
    print(title)
    #匹配需要的串
    image_pattern = re.compile('gallery: JSON.parse\("(.*?)"\),', re.S)
    result = re.search(image_pattern, html)
    if result:
        #group(1)只匹配括号里的，group()返回包括括号里的整个串
        data = json.loads(result.group(1).replace('\\', ''))
        # print(data)
        if data and 'sub_images' in data.keys():
            sub_imges = data['sub_images']
            # 获得图片的url
            images = [item.get('url') for item in sub_imges]
            # 下载图片
            for image in images:
                download_image(image)
            #返回预备要存入MongoDB的json串
            return {
                'title' : title,
                'images' : images,
                'url' : url
            }
    else:
        print("failed")

def save_to_mongo(result):
    #插入
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    else:
        return False

def download_image(url):
    print('downing', url, '...')
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # print(response.text)
            filename = url.split('/')[-1]
            #保存图片
            save_image(response, filename)
        return None
    except RequestException:
        print('请求图片出错', url)
        return None

def save_image(response, filename):
    file_path = './jiepai/{0}.{1}'.format(filename, 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            #按字节流保存
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
            f.close()

def main(offset):
    #请求index页面
    html = get_page_index(offset, '街拍')
    #解析页面
    for url in parse_page_index(html):
        #头条返回的url已经不能直接访问到网页，而是跳转到了新的页面，所以要自己转下格式
        url = 'https://www.toutiao.com/a' + url.split('/')[-2]
        # 请求detail页面
        html = get_page_detail(url)
        if html:
            #解析detail页面
            result = parse_page_detail(html, url)
            #存入数据库
            # if result:
            #     save_to_mongo(result)


if __name__ == "__main__":

    if not os.path.exists('./jiepai'):
        os.mkdir('./jiepai')
    groups = [x*20 for x in range(GROUP_START, GROUP_END+1)]
    #创建进程池，默认为cpu核数
    pool = Pool(processes=4)
    #开启进程，传入参数
    pool.map(main, groups)