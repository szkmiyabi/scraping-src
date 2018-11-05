import scrapy
from rekishiru.items import RekishiruItem
import re
import lxml.html
import requests
from urllib.request import urlopen

class Root_Spider(scrapy.Spider):
    name = 'root_spider'
    allowed_domains = ['awakouko.info']
    start_urls = ['http://awakouko.info/']

    def parse(self, response):
        for url in response.css('a::attr("href")').extract():
            yield scrapy.Request(response.urljoin(url), self.parse_titles)

    def parse_titles(self, response):
        item = RekishiruItem()
        res_str = re.sub(r"<\?xml.*?>", "", response.text)
        try:
            title = re.search(r"<title>(.*?)</title>",res_str).group(1)
        except:
            title = self.parse2(response.url)


        item["depth"] = 0
        item["title"] = title
        item["href"] = response.url
        yield item
    
    def parse2(self, url):
        f = urlopen(url)
        encoding = f.info().get_content_charset(failobj="utf-8")
        return f.read().decode(encoding)
        #print(response.text)
        #return response.text
