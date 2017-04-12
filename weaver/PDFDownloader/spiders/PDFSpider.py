import scrapy


class PDFSpider(scrapy.Spider):
    # unique spider name
    name = "quotes"

    def __init__(self):
        self.lastUrl = None

    def start_requests(self):
        # inital crawling list
        urls = [
            'https://arxiv.org/pdf/1704.03423.pdf',
            #'http://quotes.toscrape.com/page/1/',
            #'http://quotes.toscrape.com/page/2/',
        ]
        # generator call returning an iterable of requests
        for url in urls:
            self.lastUrl = url
            yield scrapy.Request(url=url, callback=self.parse)

    #method used to parse scraped responses
    def parse(self, response):
        # write httpresponse as a html file
        filename = response.url.split("/")[-1]
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        print("Parsed {}".format(self.lastUrl))