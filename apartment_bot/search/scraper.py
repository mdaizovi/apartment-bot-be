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
        BASE_URL = "https://www.immobilienscout24.de/Suche/shape/wohnung-mieten?"
        self.content = None
    
    def _open_browser(self):

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        if settings.ENV == "prod":
            browser = webdriver.Chrome(options=chrome_options)
        elif settings.ENV == "dev":
            browser = webdriver.Chrome(os.path.join(settings.BASE_DIR, 'search','chromedriver'), options=chrome_options)

        try:
            browser.get("https://www.google.com")
            print("Page title was '{}'".format(browser.title))
        finally:
            browser.quit()
        print("done")


    #---------------------------------------------------------------------------
    def _anonymous_url(self, url = None):
        """Takes full_url, returns site reading for Beautiful Soup, using requests"""
        self.content = None
        attempts = 0
        response = None
        headers = Headers(os="mac", headers=True).generate()
        if not url:
            url = self.search_url

        while not response and attempts < 5:
            try:
                attempts += 1
                response = requests.get(url, headers=headers, timeout=60)
                if response:
                    self.content = response.text
                    break
                else:
                    print("sleeping off the problem")
                    sleep(randint(60,120))
            except:
                print("problem with response")
                if attempts > 5:
                    print("\n>5 attempts")
                    print("check url\n{}\n".format(url))
                    break
                sleep_int = randint(5,10)
                sleep(sleep_int)
        return self.content

    #---------------------------------------------------------------------------
    def _protected_url(self, url):
        """Takes full_url, returns site reading for Beautiful Soup, using requests"""
        attempts = 0
        response = None

        with requests.Session() as s:
            p = s.post(self.login_url, data=payload)
            # An authorised request.
            r = s.get(url)
            self.content = r.text

        return self.content

    #-------------------------------------------------------------------------------
    def _check_listings(self):
        # go to url, save any new ones
        items = []
        self._anonymous_url()
        
        if self.content:
            soup = bs4.BeautifulSoup(self.content, "html.parser")
            if soup:
                results = soup.find(id='resultListItems')
                if results:
                    items = results.find_all("li", {"class": "result-list__listing"})
                else:
                    print("no results")
                    if "Ich bin kein Roboter - ImmobilienScout24" in soup.getText():
                        print("knows I'm a robot")
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

