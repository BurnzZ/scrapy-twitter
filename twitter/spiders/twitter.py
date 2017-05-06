import scrapy

class TwiterUserSpider(scrapy.Spider):
    name = "twitter"
    allowed_domains = ["twitter.com"]

    def __init__(self, urls=None):
        self.urls = []

        self._populate_urls(urls)


    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):

        user = response.css('h1.ProfileHeaderCard-name a::attr(href)').extract_first()
        user = user[1:] # remove preceeding slash

        for tweet in response.css('div.tweet'):
            yield {
                'tweet': tweet,
                'user': user
            }

    def _populate_urls(self, file_path):
        """This reads the file containing the urls to crawl, provided in the command line."""

        with open(file_path, 'r') as f:
            for line in f:
                self.urls.append(line.strip())
