from excrawler import Crawler
import re
from database.db import db 
from utils.log import error,info
import time
from config.configHelper import setConfig,getConfig
from excrawler import Crawler
import requests
from proxy import proxypool

pool = proxypool()
proxies = pool.getProxysequence()
r = requests.get("https://exhentai.org/",proxies = proxies)
print(r.text)