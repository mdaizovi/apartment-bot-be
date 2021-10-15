import bs4
import os
import requests
from random import randint
from time import sleep
from selenium import webdriver

from django.conf import settings
from django.shortcuts import render

from fake_headers import Headers


#===============================================================================
class Scraper:

    def __init__(self):
        self.BASE_URL = "https://www.immobilienscout24.de/Suche/shape/wohnung-mieten?"
        self.content = None
    
    def _open_browser(self, url):

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        if settings.ENV == "prod":
            browser = webdriver.Chrome(options=chrome_options)
        elif settings.ENV == "dev":
            browser = webdriver.Chrome(os.path.join(settings.BASE_DIR, 'search','chromedriver'), options=chrome_options)

        try:
            browser.get(self.BASE_URL + url)
            self.content = browser.page_source
            items = self._check_listings()
            print("%s listings found" % len(items))
            #TODO something with the listings, if they work
        finally:
            browser.quit()
        print("done")

    #-------------------------------------------------------------------------------
    def _check_listings(self):
        # go to url, save any new ones
        items = []
        
        if self.content:
            soup = bs4.BeautifulSoup(self.content, "html.parser")
            if soup:
                results = soup.find(id='resultListItems')
                if results:
                    print("there are results")
                    items = results.find_all("li", {"class": "result-list__listing"})
                else:
                    print("no results")
                    if "Ich bin kein Roboter - ImmobilienScout24" in soup.getText():
                        print("\n\nknows I'm a robot\n\n")
                        Html_file= open("immoBotPage.html","w")
                        Html_file.write(self.content)
                        Html_file.close()
            else:
                print("-----------no soup! Is there a problem?")
            return items
        else:
            print("no content?!?")
        return items     

    #-------------------------------------------------------------------------------
    def _parse_listing(self, item):

        result_id = item['data-id']
        entry_data = item.find("div", {"class": "result-list-entry__data"})
        title = entry_data.find("h5", {"class": "result-list-entry__brand-title"}).getText()
        if title.startswith("NEU"):
            title = title.replace("NEU","",1)

        criteria_div = entry_data.find("div", {"class": "grid grid-flex gutter-horizontal-l gutter-vertical-s"})
        criteria_items = criteria_div.find_all("dl")

        bdr = criteria_items[2].getText().split()[0]
        sqmeters = criteria_items[1].getText().split()[0]
        rent = criteria_items[0].getText().split()[0]
        
        landlord_div = entry_data.find("div", {"class": "result-list-entry__realtor-data-container"})
        landloard_spans = landlord_div.find_all("span", {"class": "block font-ellipsis"})
        if len(landloard_spans)>0:
            landlord = landloard_spans[0].getText()
        else:
            landlord = None
        address = entry_data.find("div", {"class": "result-list-entry__address"}).getText()

        return {"result_id":result_id, "title":title,"bdr":bdr, "sqmeters":sqmeters,"rent":rent,"landlord":landlord,"address":address}

