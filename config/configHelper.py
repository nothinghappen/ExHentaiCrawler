import configparser

cf = configparser.ConfigParser()
cf.read("config/app.conf")


def getConfig(sec, key):
    return cf.get(sec, key)

def getConfigBool(sec, key):
    return cf.getboolean(sec,key)

def getConfigInt(sec, key):
    return cf.getint(sec, key)


def setConfig(sec, key, val):
    with open("config/app.conf", "w") as conf:
        cf.set(sec, key, val)
        cf.write(conf)
