from django.db import models

#===============================================================================
class Listing(models.Model):
    result_id = models.CharField(max_length=200, null=True)
    title = models.CharField(max_length=200)
    bdr = models.CharField(max_length=3)
    sqmeters = models.CharField(max_length=100)
    rent = models.CharField(max_length=100)
    landlord = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    emailed = models.DateField(null=True, blank=True)


    #---------------------------------------------------------------------------
    @property
    def url(self):
        return "https://www.immobilienscout24.de/expose/{}/".format(self.result_id)
    
    @property
    def url_email(self):
        return "https://www.immobilienscout24.de/expose/{}/#/basicContact/email".format(self.result_id)


