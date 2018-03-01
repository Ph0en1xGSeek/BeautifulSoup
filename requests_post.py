import requests

#post提交表单内容
data = {'firstname': 'ph0en1x', 'lastname': 'geek'}
r = requests.post('http://pythonscraping.com/files/processing.php', data=data)
print(r.text)

#上传文件
file = {'uploadFile': open('./tsne-2014.png', 'rb')}
r = requests.post('http://pythonscraping.com/files/processing2.php', files=file)
print(r.text)

#cookie登录
payload = {'username': 'Ph0en1x', 'password': 'password'}
r = requests.post('http://pythonscraping.com/pages/cookies/welcome.php', data=payload)
print(r.cookies.get_dict())


r = requests.get('http://pythonscraping.com/pages/cookies/profile.php', cookies=r.cookies)#使用cookie
print(r.text)

#session 登录
session = requests.Session()
payload = {'username': 'Ph0en1x', 'password': 'password'}
r = session.post('http://pythonscraping.com/pages/cookies/welcome.php', data=payload)
print(r.cookies.get_dict())

#同一个session
r = session.get("http://pythonscraping.com/pages/cookies/profile.php")
print(r.text)