import requests
from bs4 import BeautifulSoup

URL = 'http://www.nationalgeographic.com.cn/animals/'

html = requests.get(URL).text
soup = BeautifulSoup(html, 'lxml')

img_ul = soup.find_all('ul', {'class':'img_list'})
# print(img_url)

for ul in img_ul:
    imgs = ul.find_all('img')
    for img in  imgs:
        src = img['src']
        #接收流，不需要全部接收后再存储
        r = requests.get(src, stream=True)
        img_name = src.split('/')[-1]
        with open('./img/%s' % img_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        print('Saved %s' % img_name)