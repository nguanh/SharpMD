import scrapy
from scrapy.crawler import CrawlerProcess
from weaver.models import PDFDownloadQueue
class PDFSpider(scrapy.Spider):
    # unique spider name
    name = "quotes"

    def __init__(self):
        self.lastUrl = None

    def start_requests(self):

        # generator call returning an iterable of requests
        for url in PDFDownloadQueue.objects.all():
            self.lastUrl = url.url
            #yield scrapy.Request(url=url.url, callback=self.parse)
            yield self.make_requests_from_url(url.url)


    #method used to parse scraped responses
    def parse(self, response):
        # write httpresponse as a html file
        filename = response.url.split("/")[-1]
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        print("Parsed {}".format(self.lastUrl))


def run():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(PDFSpider)
    process.start() # the script will block here until the crawling is finished