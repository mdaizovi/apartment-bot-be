import bs4
import os
import requests
from random import randint
from time import sleep

from django.conf import settings

from fake_headers import Headers



class Scraper:
    def __init__(self):
        self.login_url = "https://sso.immobilienscout24.de/sso/login?appName=is24main&source=meinkontodropdown-login&sso_return=https://www.immobilienscout24.de/sso/login.go?source%3Dmeinkontodropdown-login%26returnUrl%3D/geschlossenerbereich/start.html?source%253Dmeinkontodropdown-login&u=azhYbUpVL2E1OHNTeXpuUUdKaTB2YWdqamE3dzZwS0U5eDBuWlAxeVNLQk1JS2w5ZUJsd1ZnPT0="
        self.search_url = "https://www.immobilienscout24.de/Suche/shape/wohnung-mieten?shape=cXFyX0lnc2NwQWp6RHlzQXRgRG9vSnhoQH1sQmhiQGNgRW9JZXNBaUxzc0NBdWhIeX1CdFFpakZtRW90QmZrR2t7QHZjR2RSZHpEbGhAYGdCYmlBbn5H&haspromotion=false&numberofrooms=2.0-3.0&price=400.0-980.0&livingspace=60.0-&pricetype=calculatedtotalrent&sorting=2&enteredFrom=result_list"
        self.content = None
        self.login_payload = {
            #'inUserName': settings.IMMOBILIENSCOUT_EMAIL,
            'password': settings.IMMOBILIENSCOUT_PW
        }

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


    def _generate_email_text(self, listing):
        text_path = os.path.join(settings.BASE_DIR, 'apartments','email.txt')
        replace_dict = {"{{LANDLORD}}":listing.landlord, "{{BDR}}": listing.bdr, "{{ADDRESS}}":listing.address}
        if "Frau" in listing.landlord:
            replace_dict["{{TITLE}}"] = "geehrte"
        else:
            replace_dict["{{TITLE}}"] = "geehrter"

        f = open(text_path, "r")
        text = f.read()
        for k,v, in replace_dict.items():
            text = text.replace(k,v)
        return text

