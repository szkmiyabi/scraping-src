import requests
import lxml.html
import re
import time
from html import unescape

def main():
    datas = get_url_datas("urls.txt")
    #inks = get_link_tags(datas)
    # styles = get_style_tags(datas)
    style_attrs = get_style_attrs(datas)

    for r in style_attrs:
        print(r["pid"], r["style-attr"])
    #styles = get_style_tags(datas)

# linkタグ一覧を取得する
def get_link_tags(url_datas):
    datas = []
    for row in url_datas:
        print(row["pid"], "を処理しています。")
        time.sleep(1)
        lists = []
        res = requests.get(row["url"])
        doc = lxml.html.fromstring(res.content)
        for link in doc.cssselect("link"):
            if link.get("rel") == "stylesheet":
                lists.append(link.get("href"))
        datas.append({"pid":  row["pid"], "link-tag": lists})
    return datas

# styleタグ一覧を取得する
def get_style_tags(url_datas):
    datas = []
    for row in url_datas:
        print(row["pid"], "を処理しています。")
        time.sleep(1)
        lists = []
        res = requests.get(row["url"])
        doc = lxml.html.fromstring(res.content)
        for stl in doc.cssselect("style"):
            stlstr = lxml.html.tostring(stl)
            lists.append(stlstr)
        datas.append({
            "pid": row["pid"],
            "style-tag": lists
        })
    return datas

# style属性を取得する
def get_style_attrs(url_datas):
    datas =[]
    for row in url_datas:
        print(row["pid"], "を処理しています。")
        time.sleep(1)
        lists = []
        res = requests.get(row["url"])
        html_body = res.text
        for style_attr in re.findall(r"style=\".*?\"", html_body, re.DOTALL):
            lists.append(style_attr)
        datas.append({"pid": row["pid"], "style-attr": lists})
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