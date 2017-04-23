import requests
from bs4 import BeautifulSoup
from random import randint
from config import COOKIE,USER_AGENTS,URL,API_URL
import json

n = randint(0,len(USER_AGENTS)-1)
headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
                 'Accept-Encoding': 'gzip, deflate',
                 'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.7, ja; q=0.3',
                 'Connection': 'Keep-Alive',
                 'Host': 'exhentai.org',
                 'User-Agent': USER_AGENTS[n]}


r = requests.get(URL,cookies = COOKIE,headers = headers)

soup = BeautifulSoup(r.text,"html.parser")

def getIdAndTokenFromURL(url):
    begin = len("https://exhentai.org/g/")
    end = len(url)
    param = url[begin:end].split('/')
    return ({'gallery_id':param[0],'gallery_token':param[1]})

def getDataFromApi(gidlist):
    requestBody = {
        'method': 'gdata',
        'gidlist': [],
        'namespace': 1
    }
    requestBody['gidlist'] = gidlist
    jsonRequestBody = json.dumps(requestBody)
    r = requests.post(API_URL,data=jsonRequestBody)
    print(r.text)


#获取每个本子链接的url
tags = soup.select(".it5 > a")
gidlist = []
for tag in tags :
    href = tag['href']
    #url格式 https://e-hentai.org/g/{gallery_id}/{gallery_token}/
    #从中拿到gallery_id 与 gallery_token然后去调api获取本子详细信息
    dic = getIdAndTokenFromURL(href)
    gidlist.append([int(dic['gallery_id']),dic['gallery_token']])

getDataFromApi(gidlist)


    
