import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from itemadapter import ItemAdapter

import os
import json
import logging

logging.basicConfig(level=logging.INFO)


class Quote(Item):
    tags = Field()
    author = Field()
    quote = Field()


class Author(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


class DataPipeline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if "fullname" in adapter.keys():
            self.authors.append(dict(adapter))
        if "quote" in adapter.keys():
            self.quotes.append(dict(adapter))

    def close_spider(self, spider):
        with open("quotes.json", "w", encoding="utf-8") as fh:
            json.dump(self.quotes, fh, ensure_ascii=False, indent=2)
        with open("authors.json", "w", encoding="utf-8") as fh:
            json.dump(self.authors, fh, ensure_ascii=False, indent=2)


class QuotesSpider(scrapy.Spider):
    name = "get_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {DataPipeline: 300}}

    def parse(self, response, **kwargs):
        for q in response.xpath("//div[@class='quote']"):
            tags = q.xpath("div[@class='tags']/a/text()").extract()
            author = q.xpath("//small[@class='author']/text()").get().strip()
            quote = q.xpath("span[@class='text']/text()").get().strip()
            yield Quote(tags=tags, author=author, quote=quote)
            yield response.follow(
                url=self.start_urls[0] + q.xpath("span/a/@href").get(),
                callback=self.parse_author,
            )
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    @classmethod
    def parse_author(cls, response, **kwargs):
        content = response.xpath("//div[@class='author-details']")
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        description = content.xpath("div[@class='author-description']/text()").get().strip()

        yield Author(
            fullname=fullname,
            born_date=born_date,
            born_location=born_location,
            description=description
        )


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()

    if os.path.getsize("quotes.json") > 3000:
        logging.info(f"'quotes.json' Has been successfully filled and has size {os.path.getsize('quotes.json')}")
    else:
        logging.info(f"Data wasn't writing to the 'quotes.json'")
    if os.path.getsize("authors.json") > 3000:
        logging.info(f"'authors.json' Has been successfully filled and has size {os.path.getsize('authors.json')}")
    else:
        logging.info(f"Data wasn't writing to the 'authors.json'")
