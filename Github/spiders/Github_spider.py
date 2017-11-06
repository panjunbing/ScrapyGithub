# coding=utf-8


import scrapy
from scrapy import Request, FormRequest


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ["github.com"]
    user = ""
    password = ""
    start_urls = [""] * 5
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
        a_text = self.replace_space(response.xpath("//span[@class='Counter']/text()").extract())
        repositories, stars, followers, following = a_text[0], a_text[1], a_text[2], a_text[3]
        print "repositories:" + repositories + "  stars:" + stars + "  followers:" + followers + "  following:" + following
        return [Request(self.start_urls[1], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_repositories)]

    # 对repositories的内容进行抓取
    def scrapy_repositories(self, response):
        repositories = self.replace_space(response.xpath("//a[@itemprop='name codeRepository']/text()").extract())
        description = self.replace_space(response.xpath("//p[@itemprop='description']/text()").extract())
        programmingLanguage = self.replace_space(response.xpath("//span[@itemprop='programmingLanguage']/text()").extract())
        datetime = self.replace_space(response.xpath("//relative-time/@datetime").extract())
        for i in range(len(repositories)):
            print "\nrepositories:" + repositories[i] + "\ndescriptions:" + description[i] + "\nprogrammingLanguage:" + \
                  programmingLanguage[i] + "\ndatetime:" + datetime[i]
        return [Request(self.start_urls[2], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_stars)]

    # 对stars的内容进行抓取
    def scrapy_stars(self, response):
        repositories = self.remove_null(
            self.replace_space(response.xpath("//div[@class='d-inline-block mb-1']/h3/a/text()").extract()))
        actor = self.replace_space(response.xpath("//span[@class='text-normal']/text()").extract())
        description = self.replace_space(response.xpath("//p[@itemprop='description']/text()").extract())
        programmingLanguage = self.replace_space(
            response.xpath("//span[@itemprop='programmingLanguage']/text()").extract())
        stars_forks = self.remove_null(
            self.replace_space(response.xpath("//a[@class='muted-link mr-3']/text()").extract()))
        datetime = self.replace_space(response.xpath("//relative-time/@datetime").extract())

        # 将stars_forks奇数赋值给stars,偶数赋值给forks
        count = len(stars_forks) / 2
        stars = [""] * count
        forks = [""] * count
        i, j, k = 0, 0, 1
        while i < count:
            stars[i] = stars_forks[j]
            forks[i] = stars_forks[k]
            i, j, k = i + 1, j + 2, k + 2

        for i in range(len(repositories)):
            print "\nrepositories:" + repositories[i] + "\nactor:" + actor[i] + "\ndescription:" + description[
                i] + "\nprogrammingLanguage:" \
                  + programmingLanguage[i], "\nstars:" + stars[i] + "\nforks:" + forks[i] + "\ndatetime:" + datetime[i]
        return [Request(self.start_urls[3], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_followers)]

    # 对followers的内容进行抓取
    def scrapy_followers(self, response):
        return [Request(self.start_urls[4], meta={'cookiejar': response.meta['cookiejar']}, callback=self.scrapy_following)]

    # 对following的内容进行抓取
    def scrapy_following(self, response):
        pass

    # 去掉list中所有元素中的换行符和空格
    @staticmethod
    def replace_space(list):
        for i in range(len(list)):
            list[i] = list[i].replace("\n", "").replace(" ", "")
        return list

    # 去掉list中所有空元素
    @staticmethod
    def remove_null(list):
        while "" in list:
            list.remove("")
        return list

    # def after_login(self, response):
    #     for url in self.start_urls:
    #         yield Request(url, meta={'cookiejar': response.meta['cookiejar']})
    #

    def parse(self, response):
        pass
