import requests
import json
from config.conf import APP_ID,LOG_URL
from config.configHelper import getConfig

#从配置文件查看是否向日志服务器写日志
enable = getConfig("log","enable")

#同步写日志
def log(title,level,location,message):
    if enable == "false":
        return
    log = {
        'appid':APP_ID,
        'title':title,
        'level':level,
        'location':location,
        'message':message
    }
    request = []
    request.append(log)
    head = {'Content-Type':'application/json;charset=UTF-8'}
    try:
        res = requests.post(LOG_URL,json = request)
    finally:
        print("log fail")

def info(title,location,message):
    log(title,"info",location,message)

def debug(title,location,message):
    log(title,"debug",location,message)

def error(title,location,message):
    log(title,"error",location,message)