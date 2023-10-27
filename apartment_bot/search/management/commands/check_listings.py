from datetime import datetime
from time import sleep
from random import randint

from django.conf import settings
from django.core.management.base import BaseCommand

from apartments.tasks import check_for_new_listings

# source virtualenvwrapper.sh && workon kaffeevenv && python3.5 /home/Dahmer/kaffee/manage.py check_listings


class Command(BaseCommand):
    def handle(self, *args, **options):

        # print("--Looking for new listings")
        # while True:
        #     check_for_new_listings()
        #     sleep(6)
        #     now = datetime.now()
        #     if now.minute >= 55:
        #         print("breaking")
        #         False
        #         break
        # print("\n\n--Done")

        print("--Looking for new listings")
        check_for_new_listings()
        sleep_int = randint(5, 20)
        sleep(sleep_int)
        print("\n\n--Done")
