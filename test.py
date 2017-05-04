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

def test(n):
    time.sleep(n)
    if n == 3:
        raise RuntimeError
    return n

with ThreadPoolExecutor(max_workers = 10) as executor:
    futures = []
    futures.append(executor.submit(test,1))
    futures.append(executor.submit(test,2))
    futures.append(executor.submit(test,3))
    futures.append(executor.submit(test,4))
    wait(futures)
    for f in futures:
        print(f.result())
