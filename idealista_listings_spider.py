import datetime
import logging
from collections import OrderedDict
import scrapy
import csv
import time


request_headers = {'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                    , 'accept-encoding' : 'gzip, deflate, br'
                    , 'accept-language' : 'es-ES,es;q=0.9'
                    , 'cache-control': 'no-cache'
                    , 'pragma': 'no-cache'
                    , 'sec-fetch-dest': 'document'
                    , 'sec-fetch-mode' : 'navigate'
                    , 'sec-fetch-site' : 'none'
                    , 'sec-fetch-user' : '?1'
                    , 'sec-gpc': '1'
                    , 'upgrade-insecure-requests': '1'
                    , 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
                    }



class IdealistaListingsSpider(scrapy.Spider):
    name = 'idealista_listings'

    def __init__(self, *args, **kwargs):
        super(IdealistaListingsSpider, self).__init__(*args, **kwargs)
        # self.zone = 'delicias'
        self.zone = 'rondilla-santa-clara'
        self.houses = []



    def start_requests(self):
        urls = [f'https://www.idealista.com/venta-viviendas/valladolid/{self.zone}/pagina-1.htm']
        for url in urls:
            yield scrapy.Request(url=url, headers=request_headers)




    def parse(self, response, **kwargs):

        table_houses = response.css('article.item')

        for item in table_houses:
            self.parse_house(item)

        logging.debug(f'Page completed with {len(table_houses)}, total {len(self.houses)}')
        
        
        next_page = response.css('li[class="next"] a')

        if len(next_page) > 0 and len(table_houses) > 0:
            next_link = "https://www.idealista.com" + next_page.attrib['href']
            logging.info(f"Moving on to next page: {next_link}")
            time.sleep(2)
            yield scrapy.Request(url=next_link, headers=request_headers)



    def parse_house(self, item):
        this_house = OrderedDict()
        try:
            this_house['crawl_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            this_house['crawl_datetime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            this_house['id'] = item.attrib['data-adid']
            this_house['name'] = item.css('div.item-info-container a.item-link').attrib['title'].strip().replace(',',';').replace('\n', '.')
            this_house['price'] = item.css('span.item-price').xpath('text()')[-1].get()
            this_house['url'] = item.css('div.item-info-container a.item-link').attrib['href']
            this_house['rooms'] = item.css('div.item-detail-char span.item-detail')[0].xpath('text()')[-1].get().strip()
            this_house['m2'] = item.css('div.item-detail-char span.item-detail')[1].xpath('text()')[-1].get().strip()
            this_house['height'] = item.css('div.item-detail-char span.item-detail')[2].xpath('text()')[-1].get().strip()
            this_house['type'] = item.css('div.item-detail-char span.item-detail small')[-1].xpath('text()')[-1].get().strip()
            this_house['elevator'] =  "yes" if "con ascensor" in this_house['type'] else "no"
            this_house['seller_phone'] = item.css('span.icon-phone')[0].xpath('text()')[-1].get().strip()
            this_house['description'] = item.css('div.description p')[0].xpath('text()')[-1].get().strip().replace(',',';').replace('\n', '.')
            this_house['seller'] = item.css('div.item-info-container picture a').attrib['title']
            this_house['seller_url'] = item.css('div.item-info-container picture a').attrib['href']


            logging.info(f"House parsed: {this_house}")
        except Exception as e:
            logging.info(f"Exception when parsing house {this_house}, exception {e}")
        print(this_house)
        self.houses += [this_house]

    def closed(self, reason):
        logging.info(f"Finished scrapping (reason={reason}) with {len(self.houses)} houses")
        logging.info(f"Writing to Csv")

        if self.houses:
            filename = f"data/houses_{self.zone}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w') as f:
                dict_writer = csv.DictWriter(f, fieldnames=self.houses[0].keys(), dialect=csv.excel)
                dict_writer.writeheader()
                dict_writer.writerows(self.houses)
                print(self.houses)
        else:
            logging.warn("No house crawled")


