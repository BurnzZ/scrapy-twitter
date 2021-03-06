# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import os
import json

from scrapy.exceptions import DropItem
from scrapy.conf import settings

class FilterTweetsPipeline(object):
    """This drops items that are either of the following:
        * retweets
        * tweet having content less than the specified in the settings
    """

    def __init__(self):
        self.min_tweet_length = settings['MIN_TWEET_LENGTH']


    def process_item(self, item, spider):

        tweet = item['tweet']

        if not self._is_retweet(tweet):
            raise DropItem("item is a retweet.")

        if not self._has_enough_content(tweet, self.min_tweet_length):
            raise DropItem("item has less than {} characters.".format(self.min_tweet_length))

        return item


    def _is_retweet(self, tweet):
        """This determines if a certain tweet is a retweet since it contains the 'data-retweet-id' attribute.

        :returns: True if tweet is a retweet; False otherwise
        """

        if tweet.css('::attr(data-retweet-id)').extract_first() is None:
            return True
        return False


    def _has_enough_content(self, tweet, length):
        """This returns False if a tweet contains characters which are less than the specified length."""

        content = tweet.css('p.tweet-text::text').extract_first()

        if content is None or len(content) < length:
            return False
        return True


class DataShapePipeline(object):
    """This extracts the necessary text-data from the Selectors returned by Spiders."""
    
    def process_item(self, item, spider):

        data = {
            'tweet_id': item['tweet'].css('::attr(data-tweet-id)').extract_first(),
            'user': item['user'],
            'time_epoch':item['tweet'].css('span._timestamp::attr(data-time)').extract_first(),
            'tweet': ''.join(item['tweet'].css('p.tweet-text ::text').extract())
        }

        return data


class CleanTweetsPipeline(object):
    """This removes unnecessary texts in tweet texts."""

    # any substrings matched in these regexes are removed from the tweet itself
    REGEX = [
        # This matches urls starting in 'http'
        re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),

        # This are for the links included in tweets with images uploaded
        re.compile(r'pic\.twitter\.com\/[a-zA-Z1-9]+')
    ]

    def process_item(self, item, spider):

        for rgx in self.REGEX:
            match = rgx.search(item['tweet'])

            if match is not None:
                item['tweet'] = rgx.sub('', item['tweet'])
                spider.log("'{0}' has been removed from the tweet.".format(match.group()))
       
        return item
     

class FileSavePipeline(object):
    """This pipeline saves the data parsed into a file"""

    def __init__(self):
        self.save_path = settings['SAVE_PATH']['tweets']
        self.output_file = os.path.join(self.save_path, 'output.json')


    def open_spider(self, spider):
        self.file = open(self.output_file, 'w')


    def close_spider(self, spider):
        self.file.close()


    def process_item(self, item, spider):
        self._write_to_file(item)
        return item


    def _write_to_file(self, item):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
