import logging
from scrapy.crawler import CrawlerProcess

from idealista_listings_spider import IdealistaListingsSpider

LOG_FORMAT = '%(asctime)-15s| %(levelname)-7s| %(name)s | %(message)s'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
REFERER = 'https://www.google.com'


request_headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
                    , 'Cache-Control': 'no-cache'
                    , 'referer': 'https://www.idealista.com/venta-viviendas/valladolid/'
                    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logging.info(f"Crawling idealista")

    process = CrawlerProcess({'USER_AGENT': USER_AGENT, 'Referer': REFERER})
    # process = CrawlerProcess(request_headers)

    process.crawl(IdealistaListingsSpider)

    process.start()
