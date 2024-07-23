import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
import time

def get_listing_info(listing_sel):
    """
    Inputs:
    listing_sel: a Selector object which contains the content
    of one listing
    Outputs:
    unit_dict: a dictionary which contains price, number of bedrooms, 
    number of bathrooms, sqft, postal code
    """
    address = listing_sel.css("a ::text").get()
    zip_code = address[-5:]
    price = listing_sel.css("div span ::text").get()[1:]
    bbs = listing_sel.css("ul li b ::text").getall()
    bed = bbs[0]
    bath = bbs[1]
    sqft = bbs[2]
    return {'address': address, 'zip_code': zip_code, 'price': price, 'num_bedrooms': bed, 
            'num_bathrooms': bath, 'sqft': sqft}

class HomePricesSpider(scrapy.Spider):
    name = "home_prices"
    allowed_domains = ["zillow.com"]
    start_urls = ["https://www.zillow.com/ma/"]
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    def parse(self, response):
       

      
        # Use Scrapy to parse the page source
        

        all_pages = response.xpath('//div[contains(@class, "StyledPropertyCardDataWrapper")]')
        next_page = "https://www.zillow.com/" +response.xpath('//ul[contains(@class, "PaginationList")]/li[contains(@class, "PaginationJumpItem")]').css('::attr(href)')[1]
        for listing in all_pages:
            yield get_listing_info(listing)
            
        yield response.follow(next_page, callback=self.parse)
        
