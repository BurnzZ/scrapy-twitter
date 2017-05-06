This is a web scraper for twitter without using its API to bypass some rate limiting.

## USAGE

`scrapy crawl twitter -a urls=url.txt`

This contains a spider called `twitter` that accepts an argument called **url** that must
contain a path to a file containing the URLs to crawl. The url file must contain a newline
delimited list of URLs.
