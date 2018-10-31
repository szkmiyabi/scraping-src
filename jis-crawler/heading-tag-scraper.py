import requests
import lxml.html
import re
import time
from pymongo import MongoClient
import sys
import html

def main():

    args = sys.argv
    dbname = args[1]
    projID = args[2]
    urlfile = args[3]

    url_datas = get_url_datas(urlfile)
    headding_report_datas = get_headding_report(url_datas)

    client = MongoClient("localhost", 27017)
    db = client[dbname]
    collection = db[projID + "-headding-rep"]
    collection.delete_many({})
    collection.insert_many(headding_report_datas)

# 見出し要素をレポートを取得する
def get_headding_report(url_datas):
    datas = []
    for row in url_datas:
        print(row["pid"], "を処理しています")
        time.sleep(1)
        try:
            res = requests.get(row["url"], verify=False)
            doc = res.text
            dom = lxml.html.fromstring(res.content)
            tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
            datas.append({
                "pid": row["pid"],
                "h1": _get_tag_list(dom, tags[0]),
                "h2": _get_tag_list(dom, tags[1]),
                "h3": _get_tag_list(dom, tags[2]),
                "h4": _get_tag_list(dom, tags[3]),
                "h5": _get_tag_list(dom, tags[4]),
                "h6": _get_tag_list(dom, tags[5]),
            })
        except requests.exceptions.SSLError:
            print(row["pid"], "はエラーのためスキップします")
    return datas

# タグのリストを取得する
def _get_tag_list(dom, tag):
    datas = []
    for  itm in dom.cssselect(tag):
        datas.append(html.unescape(lxml.html.tostring(itm).decode()))
    return datas

# urlファイルをロードする
def get_url_datas(filename):
    datas = []
    with open(filename, "r") as f:
        for row in f:
            line = row.strip()
            cols = line.split('\t')
            datas.append({"pid": cols[0], "url": cols[1]}) 
    return datas

if __name__ == "__main__":
    main()