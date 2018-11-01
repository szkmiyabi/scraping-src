import lxml.html
import requests
import re
import time
from pymongo import MongoClient
import sys
import html
import csv

def main():
    #fetch_index_page()
    save_as_csv_from_mongo("index", "index.csv")

# indexページのURLデータベース構築
def fetch_index_page():
    all_links_data = get_all_links("http://awakouko.info/")
    db_datas = []
    for r in all_links_data:
        db_datas.append({
            "title": r["title"],
            "url": r["url"]
        })
    save_as_mongo("index", db_datas)

# mongoDB/CollectionからＣＳＶに保存する
def save_as_csv_from_mongo(coll_name, csv_name):
    tmp_datas = []
    client = MongoClient("localhost", 27017)
    db = client["rekishiru"]   
    coll = db[coll_name]
    for row in coll.find({"url": {"$ne": None}}):
        tmp_datas.append({
            "title": row["title"],
            "url": row["url"]
        })
    with open(csv_name, "w", newline="", encoding="cp932") as f:
        writer = csv.DictWriter(f, ["title", "url"])
        writer.writeheader()
        writer.writerows(tmp_datas)

# mongoDBに保存する
def save_as_mongo(collname, datas):
    client = MongoClient("localhost", 27017)
    db = client["rekishiru"]
    coll = db[collname]
    coll.delete_many({})
    coll.insert_many(datas)

# currentURLのリンク一覧を取得
def get_all_links(url):
    datas = []
    res = requests.get(url)
    content = reki_decode(res.text)
    dom = lxml.html.fromstring(content)
    dom.make_links_absolute(res.url)
    for a in dom.cssselect("a"):
        title_str = a.text
        if title_str is None:
            title_str = untextlink_decode(a)
        datas.append({
            "title": title_str,
            "url": a.get("href")
        })
    return datas

# 非テキストリンクの処理
def untextlink_decode(elm):
    ret = html.unescape(lxml.html.tostring(elm).decode())
    ret = re.sub(r"</*a.*?>", "", ret)
    return ret

# xml宣言を削除した文字列を返す
def reki_decode(str):
    ret = re.sub(r"<\?xml.+?>", "", str)
    return ret

if __name__ == "__main__":
    main()