from django.contrib import admin
from .models import AuctionsListing, Bid,Comment

# Register your models here.
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ('id' , 'title' , 'starting_bid' , 'creator')

class BidAdmin(admin.ModelAdmin):
    list_display = ('id' , 'listing' , 'bidder' , 'amount')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id' , 'listing' , 'commenter')

admin.site.register(AuctionsListing,AuctionListingAdmin)
admin.site.register(Bid,BidAdmin)
admin.site.register(Comment,CommentAdmin)