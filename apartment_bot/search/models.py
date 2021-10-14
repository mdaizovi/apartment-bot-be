from django.db import models
from django.contrib.auth import get_user_model


#===============================================================================
class SearchUrl(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    url = models.URLField()


#===============================================================================
class Listing(models.Model):

    result_id = models.CharField(max_length=200, null=True)
    title = models.CharField(max_length=200)
    bdr = models.CharField(max_length=3)
    sqmeters = models.CharField(max_length=100)
    rent = models.CharField(max_length=100)
    landlord = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    search_url = models.ForeignKey(SearchUrl, on_delete=models.CASCADE)
    user_notified = models.DateField(null=True, blank=True)


    #---------------------------------------------------------------------------
    @property
    def url(self):
        return "https://www.immobilienscout24.de/expose/{}/".format(self.result_id)
    
    @property
    def url_email(self):
        return "https://www.immobilienscout24.de/expose/{}/#/basicContact/email".format(self.result_id)


