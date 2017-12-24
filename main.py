from config.configHelper import setConfig, getConfig, getConfigInt
from excrawler import Crawler

if __name__ == "__main__":
    if getConfig("app", "old_context") != "":
        # 从上次爬取上下文中恢复爬取
        context = eval(getConfig("app", "old_context"))
        crawler = Crawler(context)
    else:
        crawler = Crawler()
    crawler.crawl()
