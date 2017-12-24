from excrawler import Crawler
import re
from database.db import db 
from utils.log import error,info
import time
from config.configHelper import setConfig,getConfig
from excrawler import Crawler
import requests
from proxy import proxypool
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

crawler = Crawler()

gidlist = crawler.getListByPage(1)
crawler.getDataFromApi(gidlist)