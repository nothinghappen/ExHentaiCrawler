class Consolelogger:

    sublogger = None

    def __init__(self, logger=None):
        self.sublogger = logger

    def doLog(self, title, level, location, message):
        print("title:" + title + "\nlevel:" + level +
              "\nlocation:" + location + "\nmessage:" + message)

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