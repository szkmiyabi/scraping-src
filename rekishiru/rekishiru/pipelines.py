# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from pymongo import MongoClient

class RekishiruPipeline(object):
    def process_item(self, item, spider):
        return item

class ValidationPipeline(object):

    def process_item(self, item, spider):
        if not item["title"]:
            raise DropItem("Missing title")
        return item

class MongoPipeline(object):

    def open_spider(self, spider):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["rekishiru"]
        if spider.name is "root_spider":
            self.collection = self.db["root"]
        elif spider.name is "d1_spider":
            self.collection = self.db["d1"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item