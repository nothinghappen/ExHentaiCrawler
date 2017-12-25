import requests
from bs4 import BeautifulSoup
from random import randint
from config.conf import COOKIE, USER_AGENTS, URL, API_URL
import json
from database.db import db
# from utils.cache import cache
import time
from utils.log import error, info
from exception.error import Networkerror, ParseError
import re
from config.configHelper import setConfig, getConfig, getConfigInt
from proxy import proxypool
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait


def getRandomHead():
    n = randint(0, len(USER_AGENTS) - 1)
    headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.7, ja; q=0.3',
               'Connection': 'Keep-Alive',
               'Host': 'exhentai.org',
               'User-Agent': USER_AGENTS[n]}
    return headers

# 从url字符串中解析出gallery_id与gallery_token
def getIdAndTokenFromURL(url):
    begin = len("https://exhentai.org/g/")
    end = len(url)
    param = url[begin:end].split('/')
    return ({'gallery_id': param[0], 'gallery_token': param[1]})


# 封装请求重试与异常处理，记录日志的代码
def invokeRequest(log, location, func, *args, **kwargs):
    errorCount = 0
    # 发生异常时最多重试10次
    while True:
        if errorCount >= 10:
            raise Networkerror(log + "时重试10次失败")
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            error("异常", location, log + "时网络超时")
            errorCount += 1
        except requests.exceptions.ConnectionError:
            error("异常", location, log + "时发生网络异常")
            errorCount += 1
        except Exception as e:
            error("异常", location, log + "时发生未知异常:" + str(e))
            errorCount += 1

# 判断当前网页是不是最后一页


def isLastPage(html):
    if "No hits found" in html:
        return True
    else:
        return False


def makeContext():
    return {'currentPage': 0, 'currentPosted': int(time.time()), 'newestPosted': 0}


def makeContextFromDB(db):
    # db = db()
    mangaCount = db.getCountEromanga()
    currentPage = int(mangaCount / 25)
    if mangaCount % 25 == 0:
        currentPage -= 1
    currentPosted = db.getLastPosted()
    return {'currentPage': currentPage, 'currentPosted': currentPosted}


def isUseProxy():
    return getConfig("app", "proxyEnable") == "true"


class Crawler:

    db = db()

    pool = proxypool()

    # 保存当前爬取状态的上下文
    context = {}

    def __init__(self, context=None):
        if context is None:
            self.context = makeContext()
            self.context['newestPosted'] = self.db.getNewestPosted()
        else:
            self.context = context

    # 正在爬取的本子列表当前页码
    currentPage = 0

    # 随机等0~3秒
    def wait(self):
        n = randint(0, 3)
        time.sleep(n)

    # 得到指定页码的本子列表(页码从0开始)
    def getListByPage(self, page):
        url = URL
        if page != 0:
            url = url + "?page=" + str(page)
        headers = getRandomHead()
        gidlist = []
        errorCount = 0
        while True:
            if errorCount >= 5:
                raise ParseError("获取第" + str(page) +
                                 "页本子列表时连续5次未能从html中解析出本子列表")

            if isUseProxy():
                r = invokeRequest("获取第" + str(page) + "页本子列表", "excrawler.getListByPage",
                                  requests.get, url, cookies=COOKIE, headers=headers, timeout=30, proxies=self.pool.getProxysequence())
            else:
                r = invokeRequest("获取第" + str(page) + "页本子列表", "excrawler.getListByPage",
                                  requests.get, url, cookies=COOKIE, headers=headers, timeout=30)
            soup = BeautifulSoup(r.text, "html.parser")

            # 获取每个本子链接的url
            tags = soup.select(".it5 > a")
            if len(tags) == 0:
                info("info", "excrawler.getListByPage", "获取第" +
                     str(page) + "页本子列表时未解析出本子列表,html:" + r.text)
                # 判断是不是已经到了最后一页
                if isLastPage(r.text):
                    info("info", "excrawler.getListByPage", "已经爬取到了最后一页")
                    break
                else:
                    errorCount += 1
                    continue
            for tag in tags:
                href = tag['href']
                # url格式 https://e-hentai.org/g/{gallery_id}/{gallery_token}/
                # 从中拿到gallery_id 与 gallery_token然后去调api获取本子详细信息
                dic = getIdAndTokenFromURL(href)
                gidlist.append([int(dic['gallery_id']), dic['gallery_token']])
            break
        print(gidlist)
        return gidlist

    def getDataFromApi(self, gidlist):
        requestBody = {
            'method': 'gdata',
            'gidlist': [],
            'namespace': 1
        }
        requestBody['gidlist'] = gidlist
        if isUseProxy():
            r = invokeRequest("调用api", "excrawler.getDataFromApi",
                              requests.post, API_URL, json=requestBody, timeout=30, proxies=self.pool.getProxysequence())
        else:
            r = invokeRequest("调用api", "excrawler.getDataFromApi",
                              requests.post, API_URL, json=requestBody, timeout=30)
        print(json.loads(r.text))
        return json.loads(r.text)

    # 获取缩略图url及图片详情页url,flag标识是否是从中断处恢复
    def getImages(self, base_url, gid, token, imageCount, flag):
        headers = getRandomHead()
        pageCount = int(imageCount / 40)
        if imageCount % 40 != 0:
            pageCount += 1
        imageUrls = []
        beginPage = 0
        tsequence = 0
        sequence = 0
        if flag:
            sequence = self.db.getLastImageSequenceByGidAndToken(
                gid, token) + 1
            tsequence = self.db.getLastThumbImageSequenceByGidAndToken(
                gid, token) + 1
            beginPage = int(sequence / 40)
            if sequence % 40 != 0:
                beginPage += 1
        for i in range(beginPage, pageCount):
            info("info", "excrawler.getImages", "开始爬取本子详情页第" +
                 str(i + 1) + "页,gid:" + str(gid) + " token:" + token)
            if i != 0:
                url = base_url + "?p=" + str(i)
            else:
                url = base_url

            errorCount = 0
            while True:
                if errorCount >= 5:
                    # 记录出现异常的本子
                    self.db.insertError(gid, token)
                    error("异常", "excrawler.getImages",
                          "ParseError:连续5次未能从本子详情页获取缩略图列表")
                    # raise ParseError("连续5次未能从本子详情页获取缩略图列表")
                try:
                    res = invokeRequest("获取本子详情页第" + str(i + 1) + "页", "excrawler.getImages",
                                        requests.get, url, cookies=COOKIE, headers=headers, timeout=30, proxies=self.pool.getProxysequence())
                except Networkerror as e:
                    self.db.insertError(gid, token)
                    error("异常", "excrawler.getImages",
                          "Networkerror:" + e.message)

                soup = BeautifulSoup(res.text, "html.parser")
                tags = soup.select("#gdt > .gdtm > div")
                if len(tags) == 0:
                    info("信息", "excrawler.getImages",
                         "本子详情页缩略图列表中没有图片,url:" + url + "html:" + res.text)
                    errorCount += 1
                    continue
                images = []
                for tag in tags:
                    timageUrl = re.findall(r"url\((.+)\)", tag['style'])[0]
                    a = tag.select("a")[0]
                    href = a['href']
                    img = {'gid': gid, 'token': token,
                           'sequence': sequence, 'url': href}
                    images.append(img)
                    sequence += 1
                    if timageUrl not in imageUrls:
                        timg = {'gid': gid, 'token': token,
                                'sequence': tsequence, 'url': timageUrl}
                        self.db.insertThumbimage(timg)
                        tsequence += 1
                        imageUrls.append(timageUrl)
                self.db.insertEroimage(images)
                break

    def crawl(self):
        try:
            self.doCrawl()
        except Networkerror as e:
            error("异常", "excrawler.crawl", "Networkerror:" + e.message)
        except ParseError as e:
            error("异常", "excrawler.crawl", "ParseError:" + e.message)
        except Exception as e:
            error("异常", "excrawler.crawl", "Exception:" + str(e))
        finally:
            setConfig("app", "old_context", str(self.context))

    def crawlNewest(self):
        try:
            self.doCrawlNewest()
        except Networkerror as e:
            error("异常", "excrawler.crawl", "Networkerror:" + e.message)
            setConfig("app", "new_context", str(self.context))
        except ParseError as e:
            error("异常", "excrawler.crawl", "ParseError:" + e.message)
            setConfig("app", "new_context", str(self.context))
        except Exception as e:
            error("异常", "excrawler.crawl", "Exception:" + str(e))
            setConfig("app", "new_context", str(self.context))

    # 获取数据
    def getMangaDataByPage(self, page):
        info("info", "excrawler.doCrawl", "爬取第" + str(page) + "页开始")
        # 获取本子列表
        gidlist = self.getListByPage(page)
        # 是否到达最后一页
        if len(gidlist) == 0:
            return None
        info("info", "excrawler.doCrawl", "已获取本子列表")
        res = self.getDataFromApi(gidlist)
        info("info", "excrawler.doCrawl", "已获取本子详细信息")
        gmetadata = res['gmetadata']
        info("info", "excrawler.doCrawl", "爬取第" + str(page) + "页结束")
        return gmetadata

    # 爬取至最后一页
    def doCrawl(self):
        flag = True
        while flag:
            futures = []
            # 并行发起请求5页
            with ThreadPoolExecutor(max_workers=5) as executor:
                for i in range(self.context['currentPage'], self.context['currentPage'] + 5):
                    futures.append(executor.submit(self.getMangaDataByPage, i))
            wait(futures)
            # 串行处理数据
            for f in futures:
                gmetadata = f.result()
                # 到了最后一页
                if gmetadata == None:
                    flag = False
                    break
                for data in gmetadata:
                    # 去重
                    if int(data['posted']) < self.context['currentPosted']:
                        self.db.insertEromanga(data)
                        self.context['currentPosted'] = int(data['posted'])
                self.context['currentPage'] += 1

    def doCrawlNewest(self):
        flag = True
        while flag:
            futures = []
            # 并行发起请求5页
            with ThreadPoolExecutor(max_workers=5) as executor:
                for i in range(self.context['currentPage'], self.context['currentPage'] + 5):
                    futures.append(executor.submit(self.getMangaDataByPage, i))
            wait(futures)
            # 串行处理数据
            for f in futures:
                gmetadata = f.result()
                for data in gmetadata:
                    # 最新本子爬取完毕
                    if int(data['posted']) <= self.context['newestPosted']:
                        info("info", "excrawler.crawlNewest",
                             "爬取到上次爬取的最新本子 posted:" + data['posted'])
                        setConfig("app", "new_context", "")
                        flag = False
                        exit()
                    # 去重
                    if int(data['posted']) < self.context['currentPosted']:
                        self.db.insertEromanga(data)
                        self.context['currentPosted'] = int(data['posted'])
                self.context['currentPage'] += 1
