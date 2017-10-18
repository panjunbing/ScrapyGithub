# coding=utf-8


import scrapy
from scrapy import Request, FormRequest


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ["github.com"]
    user = "panjunbing"
    password = "pjb3252523114_"
    start_urls = [
        "https://github.com/" + user
    ]
    # custom_settings = {
    #     "DEFAULT_REQUEST_HEADERS": {
    #         'authority': 'https://github.com/',
    #         'accept': 'application/json, text/javascript, */*; q=0.01',
    #         'accept-encoding': 'gzip, deflate',
    #         'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    #         'referer': 'https://github.com/',
    #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                       'Chrome/48.0.2564.97 Safari/537.36',
    #         'x-requested-with': 'XMLHttpRequest',
    #     },
    #     "ITEM_PIPELINES": {
    #         'Github.pipelines.GithubPipeline': 300
    #     }
    # }

    # 伪装头部
    post_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
        "Referer": "https://github.com/",
    }

    def start_requests(self):
        # 读取需要爬取的用户名和密码
        userFile = open("user.txt")
        self.user = userFile.readline().strip('\n')
        self.password = userFile.readline()
        userFile.close()

        return [Request("https://github.com/login",
                        meta={'cookiejar': 1}, callback=self.post_login)]

    def post_login(self, response):
        # 首先抓取网页中的authenticity_token
        authenticity_token = response.xpath("//input[@name='authenticity_token']/@value").extract()[0]
        utf8 = response.xpath("//input[@name='utf8']/@value").extract()[0]
        print utf8, authenticity_token
        # 模拟github的登录的Post请求
        return [FormRequest.from_response(response,
                                          url='https://github.com/session',
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.post_headers,  # 注意此处的headers
                                          formdata={
                                              'utf8': '✓',
                                              'login': 'panjunbing',
                                              'password': 'pjb3252523114_',
                                              'authenticity_token': authenticity_token
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self, response):
        for url in self.start_urls:
            yield Request(url,meta={'cookiejar': response.meta['cookiejar']})

    def parse(self, response):
        repositories = response.xpath("//a[@href='/panjunbing?tab=repositories']/span/text()").extract()[0]
        stars = response.xpath("//a[@href='/panjunbing?tab=stars']/span/text()").extract()[0]
        followers = response.xpath("//a[@href='/panjunbing?tab=followers']/span/text()").extract()[0]
        following = response.xpath("//a[@href='/panjunbing?tab=following']/span/text()").extract()[0]
        print repositories,stars,followers,following