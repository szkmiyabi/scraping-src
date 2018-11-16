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
        # add write
        self.base_url = "http://awakouko.info/modules/piCal/"
    
    def fetch(self):
        datas = []
        res = requests.get(self.url)
        dom = lxml.html.fromstring(self.reki_decode(res.text))
        datas.append({
            "key_addr": "---",
            "title": dom.cssselect("title")[0].text,
            "url": self.url
        })

        for r in dom.cssselect("a"):
            title_str = r.text
            title_url = r.get("href")
            if self.is_raise_link(title_url):
                continue
            if title_str is None:
                title_str = self.untextlink_decode(r)
                if self.is_empty_link(title_str):
                    continue
            if title_str == "":
                    continue
            datas.append({
                "key_addr": self.url,
                "title": title_str.strip(),
                "url": title_url
            })
        return datas

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
            writer = csv.DictWriter(f,  ["key_addr", "title", "url"], delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
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

class CalSpider(OneSpider):

    # override
    def fetch(self):
        datas = []
        res = requests.get(self.url)
        dom = lxml.html.fromstring(self.reki_decode(res.text))
        datas.append({
            "key_addr": "---",
            "title": dom.cssselect("title")[0].text + self.get_month_title(),
            "url": self.url
        })
        datas.extend(self.get_calendar_td_link_datas(dom))
        datas.extend(self.get_under_link_datas(dom))
        return datas

    # カレンダーのスケジュールリンクを取得
    def get_calendar_td_link_datas(self, dom_obj):
        datas = []
        for td in dom_obj.xpath('//*[@id="ModuleContents"]/table[1]/tr/td/table[2]/tr/td'):
            td_tag = html.unescape(lxml.html.tostring(td).decode())
            td_tag = self.table_tag_raise(td_tag)
            for aline in re.findall(r'<a.+?>.+?</a>', td_tag, re.DOTALL):
                if self.is_calendar_td_raise_link(aline):
                    continue
                else:
                    atag_text = self.fetch_atag_text(aline)
                    atag_url = self.fetch_atag_href(aline)
                    datas.append({
                        "key_addr": self.url,
                        "title": atag_text,
                        "url": self.base_url + atag_url
                    })
        return self.make_uniq_datas(datas)
    
    # カレンダー下のスケジュールリンクを取得
    def get_under_link_datas(self, dom_obj):
        datas = []
        for row in dom_obj.xpath('//*[@id="ModuleContents"]/table[2]/tr/td[2]/table/tr/td/a'):
            atag = html.unescape(lxml.html.tostring(row).decode())
            atag_text = self.fetch_atag_text(atag)
            atag_url = self.fetch_atag_href(atag)
            datas.append({
                "key_addr": self.url,
                "title": atag_text,
                "url": self.base_url + atag_url
            })
        return datas

    # urlが重複しているデータを除去
    def make_uniq_datas(self, datas):
        chkurls= []
        ret_datas = []
        for r in datas:
            url = r["url"]
            if len(chkurls) < 1:
                chkurls.append(url)
                ret_datas.append(r)
            else:
                tmp = list(set(chkurls))
                if url not in tmp:
                    chkurls.append(url)
                    ret_datas.append(r)
                else:
                    continue
        return ret_datas

    def get_month_title(self):
        param = re.search(r'(\?caldate=)([0-9]+?)-([0-9]+?)-([0-9]+)', self.url)
        return param.group(2) + "年" + param.group(3) + "月"

    def table_tag_raise(self, htmlstr):
        return re.sub(r'<table.*?>.+</table>', "", htmlstr)

    def fetch_atag_text(self, tagstr):
        return re.search(r'<a.*?>(.*?)</a>', tagstr).group(1)

    def fetch_atag_href(self, tagstr):
        return re.search(r'href="(.*?)"', tagstr).group(1)
    
    def is_calendar_td_raise_link(self, htmlstr):
        flg = False
        if re.search(r'(src=".+)(week_index|spacer)(\.gif")', htmlstr):
            flg = True
        elif re.search(r'(class="calbody")', htmlstr):
            flg = True
        return flg

args = sys.argv
url = args[1]
spy = CalSpider(url, True, False)
spy.save_as_csv(spy.fetch(), "cp932")





