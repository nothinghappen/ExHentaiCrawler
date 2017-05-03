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

def add(a,b):
    time.sleep(5)
    raise RuntimeError
    print(a+b)
    return a+b

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = []
    futures.append(executor.submit(add,1,2))
    futures.append(executor.submit(add,1,2))
    futures.append(executor.submit(add,1,2))
    futures.append(executor.submit(add,1,2))
    futures.append(executor.submit(add,1,2))   
    wait(futures)
    futures[0].result()
    print("finish")
