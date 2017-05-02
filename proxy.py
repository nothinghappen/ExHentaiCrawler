from config.conf import PROXIESPOOL
from random import randint

class proxypool:
    n = 0
    l = len(PROXIESPOOL)

    def getProxysequence(self):
        proxies = {
            "https": "http://" + PROXIESPOOL[self.n] + "/"
        }
        self.n = (self.n + 1) % self.l
        return proxies

    def getProxyRandom(self):
        ri = randint(0,self.l - 1)
        proxies = {
            "https": "http://" + PROXIESPOOL[ri] + "/"
        }
        return proxies