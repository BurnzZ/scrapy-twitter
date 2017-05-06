import re
import json
import scrapy

from scrapy.selector import Selector

class TwiterUserSpider(scrapy.Spider):
    name = "twitter"
    allowed_domains = ["twitter.com"]

    def __init__(self, urls=None):
        self.page_position_rgx = re.compile(r'data-min-position="([^"]+?)"')
        self.scroll_content = 'https://twitter.com/i/profiles/show/{user}' \
                '/timeline/tweets?include_available_features=1' \
                '&include_entities=1&max_position={page_position}' \
                '&reset_error_state=false'

        self.urls = []
        self._populate_urls(urls)


    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        user = self._get_user(response)

        for tweet in self._yield_tweets(user, response):
            yield tweet

        for tweet in self._load_scroll_content(user, response):
            yield tweet


    def _load_scroll_content(self, user, response, page_position=None):
        """Twiter has an infinite scroll style of loading more tweets on a single page.

        This triggers that dynamic content loading.
        """

        url_for_scroll_load = self._get_scroll_url(user, response, page_position)

        request = scrapy.Request(url=url_for_scroll_load, callback=self.parse_scroll_content)
        request.meta['user'] = user
        yield request


    def parse_scroll_content(self, response):

        user = response.meta['user']

        raw_scroll_data = json.loads(response.body)

        html_page = Selector(text=raw_scroll_data['items_html'])
        page_position = raw_scroll_data['min_position']

        for tweet in self._yield_tweets(user, html_page):
            yield tweet

        for tweet in self._load_scroll_content(user, response, page_position):
            yield tweet

    
    def _yield_tweets(self, user, response):
        for tweet in response.css('div.tweet'):
            yield {
                'tweet': tweet,
                'user': user
            }


    def _get_scroll_url(self, user, response, page_position=None):
        """This returns the URL that contains the next set of tweet data."""

        if page_position is None:
            page_position = self._get_page_position(response)

        return self.scroll_content.format(user=user, page_position=page_position)


    def _get_page_position(self, response):
        """This parses the crawled response content to find and return the number contained in data-min-positon."""

        rgx_match = self.page_position_rgx.search(response.body.decode('utf-8'))
        captured_groups = rgx_match.groups()

        if len(captured_groups) > 0:
            return captured_groups[0]


    def _get_user(self, response):
        """On the base page of the requested URL, this returns the username that belongs to the URL."""

        user = response.css('h1.ProfileHeaderCard-name a::attr(href)').extract_first()
        return user[1:] # remove preceeding slash


    def _populate_urls(self, file_path):
        """This reads the file containing the urls to crawl, provided in the command line."""

        with open(file_path, 'r') as f:
            for line in f:
                self.urls.append(line.strip())
