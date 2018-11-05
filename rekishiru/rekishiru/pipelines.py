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
            item["title"] = "title none"
        return item

class MongoPipeline(object):

    def open_spider(self, spider):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["rekishiru"]
        self.collection = self.db["sitemap"]
        self.collection.delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item