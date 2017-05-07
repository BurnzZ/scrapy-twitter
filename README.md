This is a web scraper for fetching tweets from a list of user accounts,
without using twitter's API to avoid its rate limiting.

## USAGE

`scrapy crawl twitter -a urls_file=url.txt -a urls_link=https://pastebin.com/raw/XXX123 -a combine_urls=True`

**Parameters**|**Description**
:-----:|:-----:
urls_file|local path to file
urls_link|link to an online resource
combine_urls|*Optional*. Links from both *urls_file* and *urls_link* are combined. *Default: False*

Both `urls_file` and `urls_link` must only contain links which are newline separated.

## MOTIVATION

I use this personally to keep track of twitter users who consistently tweet stock trading
speculations for the **Philippine Stock Exchange** (*PSE*). Spiders in this project are
deployed on my personal Scrapinghub platform.
