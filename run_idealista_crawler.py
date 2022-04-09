import logging
from scrapy.crawler import CrawlerProcess

from idealista_listings_spider import IdealistaListingsSpider

LOG_FORMAT = '%(asctime)-15s| %(levelname)-7s| %(name)s | %(message)s'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logging.info(f"Crawling idealista")

    process = CrawlerProcess()

    process.crawl(IdealistaListingsSpider)

    process.start()
