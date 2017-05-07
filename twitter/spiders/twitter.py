import re
import json
import scrapy
import requests

from scrapy.selector import Selector

class TwiterUserSpider(scrapy.Spider):
    name = "twitter"
    allowed_domains = ["twitter.com"]

    def __init__(self, urls_file=None, urls_link=None, combine_urls=False):
        self.page_position_rgx = re.compile(r'data-min-position="([^"]+?)"')
        self.scroll_content = 'https://twitter.com/i/profiles/show/{user}' \
                '/timeline/tweets?include_available_features=1' \
                '&include_entities=1&max_position={page_position}' \
                '&reset_error_state=false'

        self.urls = self._populate_urls(urls_file, urls_link, combine_urls)


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

        if raw_scroll_data['has_more_items'] is False:
            return 

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


    def _populate_urls(self, urls_file, urls_link, combine_urls):
        """This return the list urls to crawl based on the arguments provided in the command line.

        Moreover, urls from both resources can be opted to be combined or not via the `combine` boolean flag.
        Combining them would need both url resource arguments to be present.

        Consequently, if `combine_urls` is set to False, it takes the following precedence based on availability:
            1. FILE
            2. LINK
        """

        from_file = self._read_url_file(urls_file)
        from_link = self._read_url_link(urls_link)
        
        if combine_urls:
            if not (from_file and from_link):
                raise AttributeError("URL resources from file and link must both be present to combine.")
            return list(set(from_file + from_link))

        # not combining URLS would have employ the precedence
        return from_file or from_link


    def _read_url_file(self, urls_file):
        if urls_file is None:
            return None

        urls = []

        with open(urls_file, 'r') as f:
            for line in f:
                urls.append(line.strip())

        return urls


    def _read_url_link(self, urls_link):
        if urls_link is None:
            return None

        req = requests.get(urls_link)

        if req.status_code != 200:
            return None

        return [url.strip() for url in req.text.split('\n')]
