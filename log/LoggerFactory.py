from log import Consolelogger,ServerLogger
from config.configHelper import getConfig

def getLogger(config):
    # 从配置文件查看是否启动日志记录
    enable = getConfig("log", "enable")
    # 是否向控制台写日志
    toconsole = getConfig("log", "toconsole")
    # 是否向日志服务器写日志
    toserver = getConfig("log", "toserver")

    logger = None

    if toconsole:
        logger = Consolelogger(logger)

    if toserver:
        logger = ServerLogger(logger)

    return logger