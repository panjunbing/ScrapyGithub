# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubItem(scrapy.Item):

    user = scrapy.Field()                                   #用户名
    repositories = scrapy.Field()
    stars = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()

    pass