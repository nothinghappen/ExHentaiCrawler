from database.db import db
import time
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
from NetWork.Request import Request
from log import LoggerFactory
import re
from config.configHelper import setConfig, getConfig, getConfigInt
from proxy import proxypool
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait


class Excrawler:

    interval = 3
    logger = None
    request = None
    db = None

    # 保存当前爬取状态的上下文
    context = {}

    def makeContext(self):
        return {'currentPage': 0, 'currentPosted': int(time.time()), 'newestPosted': 0}

    # 从url字符串中解析出gallery_id与gallery_token
    def getIdAndTokenFromURL(self, url):
        begin = len("https://exhentai.org/g/")
        end = len(url)
        param = url[begin:end].split('/')
        return ({'gallery_id': param[0], 'gallery_token': param[1]})

    def isLastPage(self, html):
        if "No hits found" in html:
            return True
        else:
            return False


    def wait(self):
        time.sleep(self.interval)

    def __init__(self, context=None):

        self.logger = LoggerFactory.getLogger(None)
        self.request = Request(self.logger)

        if context is None:
            self.context = self.makeContext()
            # self.context['newestPosted'] = self.db.getNewestPosted()
        else:
            self.context = context

            # 得到指定页码的本子列表(页码从0开始)

    def getListByPage(self, page):
        url = URL
        if page != 0:
            url = url + "?page=" + str(page)

        gidlist = []

        errorCount = 0
        while True:
            if errorCount >= 5:
                raise ParseError("获取第" + str(page) +
                                 "页本子列表时连续5次未能从html中解析出本子列表")

            log = "获取第" + str(page) + "页本子列表"
            location = "excrawler.getListByPage"
            r = self.request.get(url ,log, location)

            soup = BeautifulSoup(r.text, "html.parser")

            # 获取每个本子链接的url
            tags = soup.select(".it5 > a")
            if len(tags) == 0:
                self.logger.info("info", "excrawler.getListByPage", "获取第" +
                     str(page) + "页本子列表时未解析出本子列表,html:" + r.text)
                # 判断是不是已经到了最后一页
                if self.isLastPage(r.text):
                    self.logger.info("info", "excrawler.getListByPage", "已经爬取到了最后一页")
                    break
                else:
                    errorCount += 1
                    continue

            for tag in tags:
                href = tag['href']
                # url格式 https://e-hentai.org/g/{gallery_id}/{gallery_token}/
                # 从中拿到gallery_id 与 gallery_token然后去调api获取本子详细信息
                dic = self.getIdAndTokenFromURL(href)
                gidlist.append([int(dic['gallery_id']), dic['gallery_token']])
            break

        self.logger.debug("debug","getListByPage",str(gidlist))

        return gidlist

    def getDataFromApi(self, gidlist):
        requestBody = {
            'method': 'gdata',
            'gidlist': [],
            'namespace': 1
        }
        requestBody['gidlist'] = gidlist

        log = "调用api"
        location = "excrawler.getDataFromApi"
        r = self.request.post(API_URL, requestBody, log, location)
        result = json.loads(r.text)

        self.logger.debug("debug","getDataFromApi",str(result))
        return result

