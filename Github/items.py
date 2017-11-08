# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubItem(scrapy.Item):

    # overview界面
    user = scrapy.Field()                                   #用户名
    repositories = scrapy.Field()
    stars = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()
    type = scrapy.Field()

    # repositories界面
    repositories_name = scrapy.Field()
    repositories_description = scrapy.Field()
    repositories_programmingLanguage = scrapy.Field()
    repositories_datetime = scrapy.Field()

    # star界面
    star_name = scrapy.Field()
    star_actor = scrapy.Field()
    star_description = scrapy.Field()
    star_programmingLanguage = scrapy.Field()
    star_datetime = scrapy.Field()
    star_stars = scrapy.Field()
    star_forks = scrapy.Field()

    # followers界面
    followers_name = scrapy.Field()
    followers_userName = scrapy.Field()
    followers_bio = scrapy.Field()
    followers_school = scrapy.Field()
    followers_loction = scrapy.Field()

    # following界面
    following_name = scrapy.Field()
    following_userName = scrapy.Field()
    following_bio = scrapy.Field()
    following_school = scrapy.Field()
    following_loction = scrapy.Field()

    pass
