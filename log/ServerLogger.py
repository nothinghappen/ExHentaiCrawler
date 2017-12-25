import requests
import json
from config.conf import APP_ID, LOG_URL


class Consolelogger:

    sublogger = None

    def __init__(self, logger=None):
        self.sublogger = logger

    def doLog(self, title, level, location, message):
        log = {
            'appid': APP_ID,
            'title': title,
            'level': level,
            'location': location,
            'message': message
        }
        request = []
        request.append(log)
        head = {'Content-Type': 'application/json;charset=UTF-8'}
        try:
            res = requests.post(LOG_URL, json=request)
        except:
            print("log fail")

    def log(self, title, level, location, message):

        if(sublogger is not None):
            sublogger.log(title,level,location,message)

        self.doLog(title, level, location, message)

    def info(title, location, message):
        log(title, "info", location, message)


    def debug(title, location, message):
        log(title, "debug", location, message)


    def error(title, location, message):
        log(title, "error", location, message)