import requests

from django.conf import settings
from django.utils import timezone

from .models import Listing
from .scraper import Scraper


def check_for_new_listings():
    scraper = Scraper()
    items = scraper._check_listings()
    print("listings checked: {} items".format(len(items)))
    for item in items:
        item_dict = scraper._parse_listing(item)

        listing, created = Listing.objects.get_or_create(result_id=item_dict["result_id"])
        if created:
            for k,v in item_dict.items():
                setattr(listing, k,v)

            # Send myself a telegram message
            output_target = "-442746676"
            output_content = listing.url
            url = "https://api.telegram.org/bot{}/{}".format(settings.TELEGRAM_BOT_TOKEN, "sendMessage")
            data = {"chat_id": output_target, "text": output_content, "parse_mode": "Markdown"}
            requests.post(url,data=data)

            listing.save()
