import requests
from config.conf import COOKIE, USER_AGENTS
from exception.error import Networkerror
from random import randint

def getRandomHead():
    n = randint(0, len(USER_AGENTS) - 1)
    headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.7, ja; q=0.3',
               'Connection': 'Keep-Alive',
               'Host': 'exhentai.org',
               'User-Agent': USER_AGENTS[n]}
    return headers

class Request:

    cookie = COOKIE
    # 发生异常时重试次数
    retry = 10
    logger = None

    def __init__(self, logger, retry = 10):
        self.retry = retry
        self.logger = logger

    # 封装请求重试与异常处理，记录日志的代码
    def invokeRequest(self, log, location, func, *args, **kwargs):
        errorCount = 0
        # 发生异常时重试
        while True:
            if errorCount >= self.retry:
                raise Networkerror(log + "时重试10次失败")
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout:
                self.logger.error("异常", location, log + "时网络超时")
                errorCount += 1
            except requests.exceptions.ConnectionError:
                self.logger.error("异常", location, log + "时发生网络异常")
                errorCount += 1
            except Exception as e:
                self.logger.error("异常", location, log + "时发生未知异常:" + str(e))
                errorCount += 1

    def get(self, url, log, location):
        return self.invokeRequest(log, location,
            requests.get, url, cookies=COOKIE, headers=getRandomHead(), timeout=30)

    def post(self, url, requestBody, log, location):
        return self.invokeRequest(log, location,
            requests.post, url, json=requestBody, timeout=30)
   
    
    