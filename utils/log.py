import requests
import json
from config.conf import APP_ID,LOG_URL
from config.configHelper import getConfig

#从配置文件查看是否启动日志记录
enable = getConfig("log","enable")
#是否向控制台写日志
toconsole = getConfig("log","toconsole")
#是否向日志服务器写日志
toserver = getConfig("log","toserver")

#同步写日志
def log(title,level,location,message):
    if enable == "false":
        return
    
    if toconsole == "true":
        print("title:" + title + "\nlevel:" + level + "\nlocation:" + location + "\nmessage:" + message)
    
    if toserver != "true":
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
    except:
        print("log fail")

def info(title,location,message):
    log(title,"info",location,message)

def debug(title,location,message):
    log(title,"debug",location,message)

def error(title,location,message):
    log(title,"error",location,message)