import requests
from bs4 import BeautifulSoup
from random import randint
from config.conf import COOKIE,USER_AGENTS,URL,API_URL
import json
from api import getDataFromApi
from database.db import insert,getConnection
from utils.cache import cache
import time

#从url字符串中解析出gallery_id与gallery_token
def getIdAndTokenFromURL(url):
    begin = len("https://exhentai.org/g/")
    end = len(url)
    param = url[begin:end].split('/')
    return ({'gallery_id':param[0],'gallery_token':param[1]})

#得到指定页码的本子列表(页码从0开始)
def getListByPage(page):
    url = URL
    if page != 0:
        url = url + "?page=" + str(page)
    n = randint(0,len(USER_AGENTS)-1)
    headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
                 'Accept-Encoding': 'gzip, deflate',
                 'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.7, ja; q=0.3',
                 'Connection': 'Keep-Alive',
                 'Host': 'exhentai.org',
                 'User-Agent': USER_AGENTS[n]}


    r = requests.get(url,cookies = COOKIE,headers = headers)
    soup = BeautifulSoup(r.text,"html.parser")

    #获取每个本子链接的url
    tags = soup.select(".it5 > a")
    gidlist = []
    for tag in tags :
        href = tag['href']
        #url格式 https://e-hentai.org/g/{gallery_id}/{gallery_token}/
        #从中拿到gallery_id 与 gallery_token然后去调api获取本子详细信息
        dic = getIdAndTokenFromURL(href)
        gidlist.append([int(dic['gallery_id']),dic['gallery_token']])
    
    return gidlist

if __name__ == "__main__":
    #缓存最新插入的100条记录，用于去重
    ca = cache(100)
    for index in range(10):
        print("爬取第"+str(index)+"页开始")
        gidlist = getListByPage(index)
        print("获取本子列表")
        res = getDataFromApi(gidlist)
        print("获取本子详细信息")
        gmetadata = res['gmetadata']
        for data in gmetadata:
            key = "%s-%s" % (data['gid'],data['token'])
            if ca.containKey(key):
                print("delete")
                gmetadata.remove(data)
            else:
                ca.put(key,None)

        connection = getConnection()
        try:
            insert(gmetadata,connection)
        finally:
            connection.close()
        print("爬取第"+str(index)+"页结束")
        time.sleep(3)
        




