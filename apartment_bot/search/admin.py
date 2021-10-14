from django.contrib import admin
from .models import Listing

#===============================================================================
class ListingAdmin(admin.ModelAdmin):

    list_display = ('bdr', 'sqmeters','rent', 'address')
    search_fields = ('sqmeters','rent', 'address')
    list_display_links = list_display
    list_filter = ('bdr',)           
    
#===============================================================================
admin.site.register(Listing, ListingAdmin)
