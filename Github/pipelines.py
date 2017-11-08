# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import json
import codecs
import MySQLdb
import MySQLdb.cursors
import copy


class MysqlGithubPipeline(object):
    @classmethod
    def from_settings(cls, settings):
        # 1、@classmethod声明一个类方法，而对于平常我们见到的则叫做实例方法。
        # 2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
        # 3、可以通过类来调用，就像C.f()，相当于java中的静态方法
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_NAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    def __init__(self, dbpool):
        self.dbpool = dbpool

    def process_item(self, item, spider):
        asynItem = copy.deepcopy(item)
        query = self.dbpool.runInteraction(self._insert_data, asynItem)
        query.addErrback(self._handle_error, item, spider)
        return item

    # 插入数据库
    @staticmethod
    def _insert_data(tx, item):
        if item["type"] == "overview":
            sql = "insert into user (user,repositories,stars,followers,following) VALUES (%s,%s,%s,%s,%s)"
            params = (item["user"], item["repositories"], item["stars"], item["followers"], item["following"])
        elif item["type"] == "repositories":
            sql = "insert into repositories (name,description,programmingLanguage,datetime) VALUES (%s,%s,%s,%s)"
            params = (item["repositories_name"], item["repositories_description"],
                      item["repositories_programmingLanguage"], item["repositories_datetime"])
        elif item["type"] == "stars":
            sql = "insert into star(name,actor,description,programmingLanguage,datetime,stars,forks)VALUES(%s,%s,%s,%s,%s,%s,%s)"
            params = (item["star_name"], item["star_actor"], item["star_description"],
                      item["star_programmingLanguage"], item["star_datetime"], item["star_stars"], item["star_forks"])
        elif item["type"] == "followers":
            sql = "insert into followers(name,userName,bio,school,loction)VALUES(%s,%s,%s,%s,%s)"
            params = (item["followers_name"], item["followers_userName"], item["followers_bio"],
                      item["followers_school"], item["followers_loction"])
        else:
            sql = "insert into following(name,userName,bio,school,loction)VALUES(%s,%s,%s,%s,%s)"
            params = (item["following_name"], item["following_userName"], item["following_bio"],
                      item["following_school"], item["following_loction"])
        tx.execute(sql, params)

    # 错误处理方法
    @staticmethod
    def _handle_error(failue, item, spider):
        print failue


class JsonGithubPipeline(object):
    def __init__(self):
        self.file = codecs.open('github.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class TxtGithubPipeline(object):
    def __init__(self):
        self.file = codecs.open('github.txt', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        txt = ""
        if item["type"] == "overview":
            txt = "  user: " + item["user"] + "\r\n  repositories: " + item["repositories"] + "\r\n  stars: " + \
                  item["stars"] + "\r\n  followers: " + item["followers"] + "\r\n  following: " + item["following"]
        elif item["type"] == "repositories":
            txt += "  name: " + item["repositories_name"] + "\r\n  description: " + item["repositories_description"] + \
                   "\r\n  programmingLanguage: " + item["repositories_programmingLanguage"] + "\r\n  datetime: " + item[
                       "repositories_datetime"]
        elif item["type"] == "stars":
            txt += "  name: " + item["star_name"] + "\r\n  actor: " + item["star_actor"] + "\r\n    description: " + \
                   item["star_description"] + "\r\n  programmingLanguage: " + item["star_programmingLanguage"] + \
                   "\r\n  datetime: " + item["star_datetime"] + "\r\n  stars: " + item["star_stars"] + "\r\n  forks: " + \
                   item["star_forks"]
        elif item["type"] == "followers":
            txt += "  name: " + item["followers_name"] + "\r\n  userName: " + item[
                "followers_userName"] + "\r\n  bio: " + \
                   item["followers_bio"] + "\r\n  school: " + item["followers_school"] + "\r\n  loction: " + item[
                       "followers_loction"]
        else:
            txt += "  name: " + item["following_name"] + "\r\n  userName: " + item[
                "following_userName"] + "\r\n  bio: " + \
                   item["following_bio"] + "\r\n  school: " + item["following_school"] + "\r\n  loction: " + item[
                       "following_loction"]

        self.file.write(txt + "\r\n\r\n")
        return item

    def spider_closed(self, spider):
        self.file.close()
