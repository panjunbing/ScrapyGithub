# coding=utf-8


import scrapy
from scrapy import Request, FormRequest


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ["www.zhihu.com"]
    phone = "15077176674"
    user = "heypanpan"
    password = "pjb3252523114_"
    start_urls = [
        "https://www.zhihu.com/people/"+user
    ]
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            'authority': 'https://github.com/',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'referer': 'https://github.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/48.0.2564.97 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        },
    }

    def start_requests(self):
        # 读取需要爬取的用户名和密码
        # userFile = open("user.txt")
        # self.phone = userFile.readline().strip('\n')
        # self.password = userFile.readline()
        # userFile.close()

        return [Request("https://www.zhihu.com/",
                        meta={'cookiejar': 1},
                        callback=self.post_login)]

    def post_login(self, response):
        # 首先抓取网页中的authenticity_token
        _xsrf = response.xpath("//input[@name='_xsrf']/@value").extract()[0]
        print _xsrf
        # 模拟github的登录的Post请求
        return [FormRequest.from_response(response,
                                          url='https://www.zhihu.com/login/phone_num',
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          formdata={
                                              'phone_num': self.phone,
                                              'password': self.password,
                                              '_xsrf': _xsrf
                                          },
                                          callback=self.after_login,
                                          dont_filter=True  # 可以重复抓取
                                          )]

    def after_login(self, response):
        for url in self.start_urls:
            yield Request(url,meta={'cookiejar': response.meta['cookiejar']})

    def parse(self, response):
        pass