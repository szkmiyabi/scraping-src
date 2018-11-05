import lxml.html
import requests
import re
import time
from pymongo import MongoClient
import sys
import html
import csv
import datetime

class OneSpider:
    def __init__(self, url, mongo_flg, debug_flg):
        self.url = url
        self.mongo_flg = mongo_flg
        self.debug_flg = debug_flg
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["rekishiru"]
        self.collection = self.db["sitemap"]

    def is_empty_link(self, str):
        if re.search(r'(anchor|arrow_up)\.png"', str):
            return True
        else:
            return False

    def is_raise_link(self, href):
        flg = False
        if isinstance(href, str):
            if re.search(r'^mailto.*', href):
                flg = True
            elif re.search(r'^#.*', href):
                flg = True
            elif re.search(r'^javascript:.*', href):
                flg = True
        return flg

    def save_as_mongo(self, datas):
        if self.collection.find({"key_addr": self.url}).count() > 0:
            print("レコードが重複しているので処理をスキップします。")
            return
        self.collection.insert_many(datas)
        if self.debug_flg is True:
            self.debug_print()

    def save_as_csv(self, datas, fileencode):
        with open(self.fetch_filename_from_datetime(), "w", newline="", encoding=fileencode, errors="replace") as f:
            writer = csv.DictWriter(f,  ["key_addr", "title", "url"])
            writer.writeheader()
            writer.writerows(datas)
        if self.mongo_flg is True:
            self.save_as_mongo(datas)

    def untextlink_decode(self, r):
        ret = html.unescape(lxml.html.tostring(r).decode())
        ret = re.sub(r"</*a.*?>", "", ret)
        return ret

    def reki_decode(self, str):
        ret = re.sub(r"<\?xml.+?>", "", str)
        return ret
    
    def debug_print(self):
        for r in self.collection.find():
            print(r["key_addr"], r["title"], r["url"])

    def fetch_filename_from_datetime(self):
        datetime_fmt = datetime.datetime.today()
        return datetime_fmt.strftime("%Y-%m-%d_%H-%M-%S") + ".csv"

class NewsSpider(OneSpider):
    #override
    def fetch(self):
        datas = []
        res = requests.get(self.url)
        dom = lxml.html.fromstring(self.reki_decode(res.text))
        datas.append({
            "key_addr": "---",
            "title": dom.cssselect("title")[0].text,
            "url": self.url
        })

        for row in dom.xpath('//*[@id="ModuleContents"]/table[2]/tr/td[1]/a[2]'):
            atg = html.unescape(lxml.html.tostring(row).decode())
            title_str = self.fetch_atag_text(atg)
            title_url = self.fetch_atag_href(atg)
            datas.append({
                "key_addr": self.url,
                "title": title_str.strip(),
                "url": title_url
            })
        return datas

    def fetch_atag_text(self, tagstr):
        return re.search(r'<a.*?>(.*?)</a>', tagstr).group(1)

    def fetch_atag_href(self, tagstr):
        return re.search(r'href="(.*?)"', tagstr).group(1)

args = sys.argv
url = args[1]
spy = NewsSpider(url, True, False)
spy.save_as_csv(spy.fetch(), "cp932")





