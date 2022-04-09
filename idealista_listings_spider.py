import datetime
import logging
from collections import OrderedDict
import scrapy
import csv
import time




class IdealistaListingsSpider(scrapy.Spider):
    name = 'idealista_listings'

    def __init__(self, *args, **kwargs):
        super(IdealistaListingsSpider, self).__init__(*args, **kwargs)
        # self.zone = 'delicias'
        self.zone = 'rondilla-santa-clara'
        self.start_urls = [f'https://www.idealista.com/venta-viviendas/valladolid/{self.zone}/pagina-1.htm']
        self.houses = []


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
            yield scrapy.Request(url=next_link)



    def parse_house(self, item):
        this_house = OrderedDict()
        try:
            this_house['id'] = item.attrib['data-adid']
            this_house['name'] = item.css('div.item-info-container a.item-link').attrib['title'].strip().replace(',','_')
            this_house['price'] = item.css('span.item-price').xpath('text()')[-1].get()
            this_house['url'] = item.css('div.item-info-container a.item-link').attrib['href']
            this_house['rooms'] = item.css('div.item-detail-char span.item-detail')[0].xpath('text()')[-1].get().strip()
            this_house['m2'] = item.css('div.item-detail-char span.item-detail')[1].xpath('text()')[-1].get().strip()
            this_house['height'] = item.css('div.item-detail-char span.item-detail')[2].xpath('text()')[-1].get().strip()
            this_house['seller'] = item.css('div.item-info-container picture a').attrib['title']
            this_house['seller_url'] = item.css('div.item-info-container picture a').attrib['href']
            this_house['seller_phone'] = item.css('span.icon-phone')[0].xpath('text()')[-1].get().strip()
            this_house['description'] = item.css('div.description p')[0].xpath('text()')[-1].get().strip()
            this_house['crawl_datetime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"House parsed: {this_house}")
        except Exception as e:
            logging.info(f"Exception when parsing house {this_house}, exception {e}")

        self.houses += [this_house]

    def closed(self, reason):
        logging.info(f"Finished scrapping (reason={reason}) with {len(self.houses)} houses")
        logging.info(f"Writing to Csv")

        if self.houses:
            filename = f"houses_{self.zone}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w') as f:
                dict_writer = csv.DictWriter(f, fieldnames=self.houses[0].keys(), dialect=csv.excel)
                dict_writer.writeheader()
                dict_writer.writerows(self.houses)
                print(self.houses)
        else:
            logging.warn("No house crawled")


