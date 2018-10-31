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
    style_report_datas = get_css_report(url_datas)

    client = MongoClient("localhost", 27017)
    db = client[dbname]
    collection = db[projID + "-css-rep"]
    collection.delete_many({})
    collection.insert_many(style_report_datas)

# css情報を取得する
def get_css_report(url_datas):
    datas = []
    for row in url_datas:
        print(row["pid"], "を処理しています")
        time.sleep(1)
        try:
            res = requests.get(row["url"], verify=False)
            doc = res.text
            dom = lxml.html.fromstring(res.content)
            link_tag_lists = []
            style_tag_lists = []
            style_attr_strs = ""
            for link in dom.cssselect("link"):
                if link.get("rel") == "stylesheet":
                    link_tag_lists.append(link.get("href"))
            for style in dom.cssselect("style"):
                style_str = html.unescape(lxml.html.tostring(style).decode())
                style_tag_lists.append(style_str)
            for style_attr in re.findall(r"style=\".*?\"", doc, re.DOTALL):
                style_attr_strs += style_attr + ","
            datas.append({
            "pid": row["pid"],
            "link-tag": link_tag_lists,
            "style-tag": style_tag_lists,
            "style-attr": style_attr_strs
            })
        except requests.exceptions.SSLError:
            print(row["pid"], "はエラーのためスキップします")
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