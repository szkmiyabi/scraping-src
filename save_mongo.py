import lxml.html
from pymongo import MongoClient

tree = lxml.html.parse("index.html")
html = tree.getroot()

client = MongoClient("localhost", 27017)
db = client.scraping          # get scraping database   (first time, create)
collection = db.links         # get links collection (first time, create)

# remove all collection
collection.delete_many({})

# css selector loop
for a in html.cssselect("a"):
    collection.insert_one({
        "url": a.get("href"),
        "title": a.text,
    })

# get registered collection order by _id
for link in collection.find().sort("_id"):
    print(link["_id"], link["url"], link["title"])

