from config.configHelper import setConfig,getConfig,getConfigInt
from excrawler import Crawler
from utils.log import error, info

if __name__ == "__main__": 
    if getConfig("app","new_context") != "":
        #从上次爬取上下文中恢复爬取
        context = eval(getConfig("app","new_context"))
        info("info","new.main","从上次爬取异常中恢复,context:" + str(context))
        crawler = Crawler(context)
    else:
        crawler = Crawler()
    crawler.crawlNewest()