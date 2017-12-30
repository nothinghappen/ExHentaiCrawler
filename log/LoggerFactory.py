from config.configHelper import getConfigBool
import requests
from config.conf import APP_ID, LOG_URL

class DummyLogger:

    def __init__(self, subLogger):
        pass

    def log(self, title, level, location, message):
        pass

class ConsoleLogger:
    subLogger = None

    def __init__(self, logger=None):
        self.subLogger = logger

    def doLog(self, title, level, location, message):
        print("title:" + title + "\nlevel:" + level +
              "\nlocation:" + location + "\nmessage:" + message)

    def log(self, title, level, location, message):
        if (self.subLogger is not None):
            self.subLogger.log(title, level, location, message)

        self.doLog(title, level, location, message)

class ServerLogger:
    subLogger = None

    def __init__(self, logger=None):
        self.subLogger = logger

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
        if self.subLogger is not None:
            self.subLogger.log(title, level, location, message)

        self.doLog(title, level, location, message)

class LogManager:

    logger = None

    def __init__(self,logger):
        self.logger = logger

    def info(self, title, location, message):
        self.logger.log(title, "info", location, message)

    def debug(self, title, location, message):
        self.logger.log(title, "debug", location, message)

    def error(self, title, location, message):
        self.logger.log(title, "error", location, message)


def getLogger(config = None):

    # 从配置文件查看是否启动日志记录
    enable = getConfigBool("log", "enable")
    # 是否向控制台写日志
    toconsole = getConfigBool("log", "toconsole")
    # 是否向日志服务器写日志
    toserver = getConfigBool("log", "toserver")

    logger = None
    
    logger = DummyLogger(logger)

    if not enable:
        return logger

    if toconsole:
        logger = ConsoleLogger(logger)

    if toserver:
        logger = ServerLogger(logger)

    logManager = LogManager(logger)

    return logManager