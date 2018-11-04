import scrapy
from rekishiru.items import MySitemap

class Root_Spider(scrapy.Spider):
    name = 'root_spider'
    allowed_domains = ['awakouko.info']
    start_urls = ['http://awakouko.info/']

    def parse(self, response):
        
        for url in response.css('a::attr("href")').extract():
            yield scrapy.Request(response.urljoin(url), self.parse_titles)
    
    def parse_titles(self, response):
        item = MySitemap()
        item["title"] = response.css("title::text").extract_first()
        item["href"] = response.url
        yield item
