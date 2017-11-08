# coding=utf-8


import scrapy
from scrapy import Request, FormRequest
from items import GithubItem


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ["github.com"]
    user = ""
    password = ""
    start_urls = [""] * 5
    items = []
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            # 'authority': 'https://github.com/',
            # 'accept': 'application/json, text/javascript, */*; q=0.01',
            # 'accept-encoding': 'gzip, deflate',
            # 'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            # 'referer': 'https://github.com/',
            # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
            #               'Chrome/48.0.2564.97 Safari/537.36',
            # 'x-requested-with': 'XMLHttpRequest',
        },
    }

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
        # 添加需要爬取的网页
        self.start_urls[0] = "https://github.com/" + self.user
        self.start_urls[1] = "https://github.com/" + self.user + "?tab=repositories"
        self.start_urls[2] = "https://github.com/" + self.user + "?tab=stars"
        self.start_urls[3] = "https://github.com/" + self.user + "?tab=followers"
        self.start_urls[4] = "https://github.com/" + self.user + "?tab=following"
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
                                              'utf8': utf8,
                                              'login': self.user,
                                              'password': self.password,
                                              'authenticity_token': authenticity_token
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self, response):
        return [Request(self.start_urls[0],
                        meta={'cookiejar': response.meta['cookiejar']},
                        callback=self.scrapy_overview)]

    # 对overview的内容进行抓取
    def scrapy_overview(self, response):
        item = GithubItem()
        a_text = self.replace_space(response.xpath("//span[@class='Counter']/text()").extract())
        item["repositories"], item["stars"], item["followers"], item["following"] = a_text[0], a_text[1], a_text[2], a_text[3]
        item["user"] = self.user
        item["type"] = "overview"
        self.items.append(item)
        return [Request(self.start_urls[1], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_repositories)]

    # 对repositories的内容进行抓取
    def scrapy_repositories(self, response):
        divs = response.xpath("//li[@class='col-12 d-block width-full py-4 border-bottom public source']")
        for i in range(len(divs)):
            item = GithubItem()
            item["repositories_name"] = self.return_1(divs[i].xpath(".//a[@itemprop='name codeRepository']/text()").extract())
            item["repositories_description"] = self.return_1(divs[i].xpath(".//p[@itemprop='description']/text()").extract())
            item["repositories_programmingLanguage"] = self.return_1(divs[i].xpath(".//span[@itemprop='programmingLanguage']/text()").extract())
            item["repositories_datetime"] = self.return_1(divs[i].xpath(".//relative-time/@datetime").extract())
            item["type"] = "repositories"
            item["user"] = self.user
            self.items.append(item)
        return [Request(self.start_urls[2], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_stars)]

    # 对stars的内容进行抓取
    def scrapy_stars(self, response):
        divs = response.xpath("//div[@class='col-12 d-block width-full py-4 border-bottom']")
        for i in range(len(divs)):
            item = GithubItem()
            item["star_name"] = self.return_1(self.remove_null(divs[i].xpath(".//div[@class='d-inline-block mb-1']/h3/a/text()").extract()))
            item["star_actor"] = self.return_1(divs[i].xpath(".//span[@class='text-normal']/text()").extract())
            item["star_description"] = self.return_1(divs[i].xpath(".//p[@itemprop='description']/text()").extract())
            item["star_programmingLanguage"] = self.return_1(divs[i].xpath(".//span[@itemprop='programmingLanguage']/text()").extract())
            item["star_datetime"] = self.return_1(divs[i].xpath(".//relative-time/@datetime").extract())
            stars_forks = self.remove_null(response.xpath("//a[@class='muted-link mr-3']/text()").extract())
            item["star_stars"], item["star_forks"] = stars_forks[0], stars_forks[1]
            item["type"] = "stars"
            item["user"] = self.user
            self.items.append(item)
        return [Request(self.start_urls[3], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_followers)]

    # 对followers的内容进行抓取
    def scrapy_followers(self, response):
        divs = response.xpath("//div[@class='d-table col-12 width-full py-4 border-bottom border-gray-light']")
        for i in range(len(divs)):
            item = GithubItem()
            item["followers_name"] = self.return_1(divs[i].xpath(".//span[@class='f4 link-gray-dark']/text()").extract())
            item["followers_userName"] = self.return_1(divs[i].xpath(".//span[@class='link-gray pl-1']/text()").extract())
            item["followers_bio"] = self.return_1(divs[i].xpath(".//p[@class='wb-break-all text-gray text-small']/text()").extract())
            item["followers_school"] = self.return_1(self.remove_null(divs[i].xpath(".//p[@class='text-gray text-small mb-0']/span/text()").extract()))
            item["followers_loction"] = self.return_1(self.remove_null(divs[i].xpath(".//p[@class='text-gray text-small mb-0']/text()").extract()))
            item["type"] = "followers"
            item["user"] = self.user
            self.items.append(item)
        return [Request(self.start_urls[4], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_following)]

    # 对following的内容进行抓取
    def scrapy_following(self, response):
        divs = response.xpath("//div[@class='d-table col-12 width-full py-4 border-bottom border-gray-light']")
        # 多维数组的创建，避免了浅拷贝
        for i in range(len(divs)):
            item = GithubItem()
            item["following_name"] = self.return_1(divs[i].xpath(".//span[@class='f4 link-gray-dark']/text()").extract())
            item["following_userName"] = self.return_1(divs[i].xpath(".//span[@class='link-gray pl-1']/text()").extract())
            item["following_bio"] = self.return_1(divs[i].xpath(".//p[@class='wb-break-all text-gray text-small']/text()").extract())
            item["following_school"] = self.return_1(self.remove_null(divs[i].xpath(".//p[@class='text-gray text-small mb-0']/span/text()").extract()))
            item["following_loction"] = self.return_1(self.remove_null(divs[i].xpath(".//p[@class='text-gray text-small mb-0']/text()").extract()))
            item["type"] = "following"
            item["user"] = self.user
            self.items.append(item)
        return self.items

    # 去掉list中所有元素中的换行符和空格
    @staticmethod
    def replace_space(arr):
        for i in range(len(arr)):
            arr[i] = arr[i].replace("\n", "").replace("\r", "").replace(" ", "")
        return arr

    # 去掉list中所有空元素,并且去掉list中所有元素中的换行符和空格
    @staticmethod
    def remove_null(arr):
        for i in range(len(arr)):
            arr[i] = arr[i].replace("\n", "").replace("\r", "").replace(" ", "")
        while "" in arr:
            arr.remove("")
        return arr

    # 返回arr第一个元素并去掉所有元素中的换行符和空格，如果第一个元素不存在则返回空
    @staticmethod
    def return_1(arr):
        if len(arr) != 0:
            arr[0] = arr[0].replace("\n", "").replace("\r", "").replace(" ", "")
            return arr[0]
        else:
            return ""

    # def after_login(self, response):
    #     for url in self.start_urls:
    #         yield Request(url, meta={'cookiejar': response.meta['cookiejar']})
    #

    def parse(self, response):
        pass
