import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner, Crawler
from scrapy.settings import Settings
from scrapy.conf import settings
from scrapy import signals
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from threading import Thread
from weaver.models import PDFDownloadQueue
from conf.config import get_config
from billiard.process import Process
import os
class PDFSpider(scrapy.Spider):
    # unique spider name
    name = "quotes"

    def __init__(self):
        self.lastUrl = None

    def start_requests(self):

        # generator call returning an iterable of requests
        for url in PDFDownloadQueue.objects.all():
            self.lastUrl = url.url
            #yield self.make_requests_from_url(url.url)
            yield scrapy.Request(url=url.url, callback=self.parse)


    #method used to parse scraped responses
    def parse(self, response):
        # write httpresponse as a html file
        filename = response.url.split("/")[-1]
        output = os.path.join(get_config("WEAVER")["pdf_path"],filename)
        # check if file exists
        if os.path.isfile(output) is False:
            with open(output, 'wb') as f:
                f.write(response.body)
            self.log('Saved file %s' % filename)
            print("Parsed {}".format(self.lastUrl))
        else:
            self.log("File {} already exists".format(output))

def run():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(PDFSpider)
    Thread(target=process.start()).start()
"""
class CrawlerScript(Process):
    def __init__(self,spider):
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider,settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        #self.crawler.configure()
        #self.spider = spider

    def run(self):
        self.crawler.crawl()
        self.crawler.start()
        reactor.run()


def run_spider():
    spider = PDFSpider()
    crawler = CrawlerScript(spider)
    crawler.start()
    crawler.join()
"""
"""
process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(PDFSpider)
def inital_run():

    process.start() # the script will block here until the crawling is finished




runner = CrawlerRunner({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
d = runner.crawl(PDFSpider)
d.addBoth(lambda _: reactor.stop())
def run():
    reactor.run()  # the script will block here until the crawling is finished
"""