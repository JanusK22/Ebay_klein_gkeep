import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerProcess, CrawlerRunner
import gkeepapi
from datetime import datetime

# <snip>
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

keep = gkeepapi.Keep()
success = keep.login('mail', 'token')

product_url = []
to_check = []

search = ["1050", "1060", "7700", "16", "8"]
preis = [100, 450]
Page = 2

message = ""
domain = "https://www.ebay-kleinanzeigen.de"
uri = []


class laptops(scrapy.Spider):
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'CONCURRENT_REQUESTS': 1,
    }

    name = "Laptop"
    base = "https://www.ebay-kleinanzeigen.de/s-notebooks/"
    for i in range(1, Page):
        uri.append(base + 'preis:' + str(preis[0]) + ':' + str(preis[1]) + ':/seite:' + str(i) + '/c278')

    def start_requests(self):
        for i in uri:
            yield scrapy.Request(i)

    def parse(self, response, _url=product_url):
        select = response.xpath('//*[@id="srchrslt-adtable"]')
        url = select.css(' a::attr(href)').extract()
        print(url)
        if len(url) != 0:
            for i in range(int(len(url) / 2) - 1):
                _url.append(domain + "" + url[2 * i])
        print(_url)
        yield url


class Infos(scrapy.Spider):
    name = "Info"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'CONCURRENT_REQUESTS': 1,
    }

    def start_requests(self):
        for i in product_url:
            yield scrapy.Request(i)

    def parse(self, response, tofind=search):
        describe = response.xpath('//*[@id="viewad-description-text"]/text()').extract()
        describe_string = ''.join(describe)
        print(describe_string)
        for i in tofind:
            if describe_string.find(i) != -1:
                to_check.append(response.request.url)
            print(to_check)
        yield to_check


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(laptops)
    yield runner.crawl(Infos)
    reactor.stop()

crawl()
reactor.run()

for i in to_check:
    message += (i + "\n")

searches = ""
for i in search:
    searches += i + ", "
now = datetime.now()

note = keep.createNote(" Ebay Suche [" + searches + "] " + str(now.strftime("%d/%m/%Y %H:%M:%S")), message)
note.color = gkeepapi.node.ColorValue.Pink
keep.sync()