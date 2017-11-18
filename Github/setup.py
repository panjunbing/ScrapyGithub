# coding=utf-8


from scrapy.crawler import CrawlerProcess
from Github.spiders.Github_spider import GithubSpider
from Github.spiders.Zhihu_spider import ZhihuSpider


spider1 = GithubSpider()
spider2 = ZhihuSpider()
process = CrawlerProcess({
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
    "Referer": "https://github.com/"})
process.crawl(spider1)
process.crawl(spider2)
process.start()






