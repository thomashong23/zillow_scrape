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

    def __init__(self, *args, **kwargs):
        super(HomePricesSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def parse(self, response):
        self.driver.get(response.url)

        wait = WebDriverWait(self.driver, 10)
        previous_length = 0

        while True:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.StyledPropertyCardDataWrapper')))
            
            # Scroll to the bottom to load more listings
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for more listings to load
            
            # Check the number of listings loaded
            current_length = len(self.driver.find_elements(By.CSS_SELECTOR, 'div.StyledPropertyCardDataWrapper'))
            
            # If no new listings are loaded, break the loop
            if current_length == previous_length:
                break

            previous_length = current_length

        # Get the page source after scrolling
        html = self.driver.page_source
        self.driver.quit()

        # Use Scrapy to parse the page source
        response = HtmlResponse(url=response.url, body=html, encoding='utf-8')

        all_pages = response.css('div.StyledPropertyCardDataWrapper')
        for listing in all_pages:
            yield get_listing_info(listing)
