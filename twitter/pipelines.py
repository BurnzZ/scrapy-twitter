# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json

from scrapy.exceptions import DropItem
from scrapy.conf import settings

class FilterTweetsPipeline(object):
    """This drops items that are either of the following:
    * retweets
    """

    def process_item(self, item, spider):

        if not self._is_retweet(item['tweet']):
            raise DropItem("Dropping a retweet.")

        return item


    def _is_retweet(self, tweet):
        """This determines if a certain tweet is a retweet since it contains the 'data-retweet-id' attribute.

        :returns: True if tweet is a retweet; False otherwise
        """

        if tweet.css('::attr(data-retweet-id)').extract_first() is None:
            return True
        return False


class CleanTweetsPipeline(object):
    """This extracts the necessary text-data from the Selectors returned by Spiders."""
    

    def process_item(self, item, spider):

        data = {}
        data['tweet_id'] = item['tweet'].css('::attr(data-tweet-id)').extract_first()
        data['user'] = item['user']
        data['time_epoch'] = item['tweet'].css('span._timestamp::attr(data-time)').extract_first()
        data['tweet'] = item['tweet'].css('p.tweet-text::text').extract_first()

        return data
     

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
