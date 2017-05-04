import scrapy


class TwiterUserSpider(scrapy.Spider):
    name = "twitter"
    allowed_domains = ["twitter.com"]
    start_urls = ['http://twitter.com/aprilleetan']

    def parse(self, response):

        user = response.css('h1.ProfileHeaderCard-name a::attr(href)').extract_first()
        user = user[1:] # remove preceeding slash

        for tweet in response.css('div.tweet'):
            yield {
                'tweet': tweet,
                'user': user
            }
