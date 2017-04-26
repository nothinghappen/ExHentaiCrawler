import requests
from bs4 import BeautifulSoup
from random import randint
from config.conf import COOKIE,USER_AGENTS,URL,API_URL
import json
from database.db import insert,getConnection
from utils.cache import cache
import time
from utils.log import error,info

def getRandomHead():
    n = randint(0,len(USER_AGENTS)-1)
    headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
                 'Accept-Encoding': 'gzip, deflate',
                 'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.7, ja; q=0.3',
                 'Connection': 'Keep-Alive',
                 'Host': 'exhentai.org',
                 'User-Agent': USER_AGENTS[n]}
    return headers

#从url字符串中解析出gallery_id与gallery_token
def getIdAndTokenFromURL(url):
    begin = len("https://exhentai.org/g/")
    end = len(url)
    param = url[begin:end].split('/')
    return ({'gallery_id':param[0],'gallery_token':param[1]})

#封装请求重试与异常处理，记录日志的代码
def invokeRequest(log,location,func,*args, **kwargs):
    errorCount = 0
    #发生异常时最多重试3次
    while True:
        if errorCount >= 3:
            print(log+"时重试3次失败")
            exit()
        try:
            return func(*args, **kwargs)
            break
        except requests.exceptions.Timeout:
            print(log+"时网络超时")
            error("异常",location,log+"时网络超时")
            errorCount += 1
        except requests.exceptions.ConnectionError:
            print(log+"时发生网络异常")
            error("异常",location,log+"时发生网络异常")
            errorCount += 1
        except :
            print(log+"时发生未知异常")
            error("异常",location,log+"时发生未知异常")
            errorCount += 1

class Crawler:

    #正在爬取的本子当前token
    currentToke = ""
    #正在爬取的本子当前gid
    currentGid = 0
    #正在爬取的本子列表当前页码
    currentPage = 0

    #得到指定页码的本子列表(页码从0开始)
    def getListByPage(self,page):
        url = URL
        if page != 0:
            url = url + "?page=" + str(page)
        headers = getRandomHead()
        r = invokeRequest("获取第"+str(page)+"页本子列表","excrawler.getListByPage",requests.get,url,cookies = COOKIE,headers = headers,timeout=30)
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

    def getDataFromApi(self,gidlist):
        requestBody = {
            'method': 'gdata',
            'gidlist': [],
            'namespace': 1
        }
        requestBody['gidlist'] = gidlist
        r = invokeRequest("调用api时","excrawler.getDataFromApi",requests.post,API_URL,json=requestBody,timeout=30)
        return json.loads(r.text)

    #获取指定链接的本子所有图片url
    def getImages(self,url):
        headers = getRandomHead()
        res = invokeRequest("获取本子详情页时","excrawler.getImages",requests.get,url,cookies = COOKIE,headers = headers)
        soup = BeautifulSoup(res.text,"html.parser")
        print(res.text)
        tag = soup.select("#gdt > .gdtm > div > a")
        if len(tag) == 0:
            print("本子详情页缩略图列表中没有图片,url:"+url)
            info("信息","excrawler.getImages","本子详情页缩略图列表中没有图片,url:"+url)
            return
        currentHref = tag[0]['href']
        re = invokeRequest("获取本子图片url时","excrawler.getImages",requests.get,currentHref,cookies = COOKIE,headers = headers)
        s = BeautifulSoup(re.text,"html.parser")
        while True:
            nxtHrefTag = s.select("#i3 > a")
            imgTag = s.select("#img")
            if len(nxtHrefTag) == 0 or len(imgTag) == 0:
                print("从url获取图片失败,url:"+currentHref)
                info("信息","excrawler.getImages","从url获取图片失败,url:"+currentHref)
                break
            nxtHref = nxtHrefTag[0]['href']
            imgUrl = imgTag[0]['src']
            print(imgUrl)
            print(nxtHref)
            if nxtHref == currentHref:
                break
            currentHref = nxtHref
            re = invokeRequest("获取本子图片url时","excrawler.getImages",requests.get,currentHref,cookies = COOKIE,headers = headers)
            s = BeautifulSoup(re.text,"html.parser")
            time.sleep(2)
    #开始爬取
    def startCrawl(self):
        #缓存最新插入的100条记录，用于去重
        ca = cache(100)
        crawler = Crawler()
        for index in range(3):
            print("爬取第"+str(index)+"页开始")
            gidlist = crawler.getListByPage(index)
            print("获取本子列表")
            res = crawler.getDataFromApi(gidlist)
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




if __name__ == "__main__":
    crawler = Crawler()
    crawler.startCrawl()
        




