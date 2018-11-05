import scrapy
from rekishiru.items import RekishiruItem
from pymongo import MongoClient

class Any_Spider(scrapy.Spider):
    name = 'any_spider'
    allowed_domains = ['awakouko.info']    
    # start_urls = ['http://awakouko.info/']

    def __init__(self, depth=0, *args, **kwargs):
        super(Any_Spider, self).__init__(*args, **kwargs)
        self.depth = int(depth)
        client = MongoClient("localhost", 27017)
        db = client["rekishiru"]
        collection = db["sitemap"]
        datas = []
        qdp = self.depth - 1
        for row in collection.find({"depth": qdp}):
            datas.append(row["href"])
        client.close()
        self.start_urls = datas

    def parse(self, response):
        for url in response.css('a::attr("href")').extract():
            yield scrapy.Request(response.urljoin(url), self.parse_titles)
    
    def parse_titles(self, response):
        item = RekishiruItem()
        item["depth"] = self.depth
        item["title"] = response.css("title::text").extract_first()
        item["href"] = response.url
        yield item