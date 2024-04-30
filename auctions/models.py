from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class AuctionsListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024,blank=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2,blank=True)
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="creator_name")
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="category_name",blank=True,null=True)
    winner = models.ForeignKey(User,on_delete=models.SET_NULL,related_name="winner",blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_winner(self,user):
        return self.winner == user if self.winner else False
    def __str__(self):
        return self.title

    
class Bid(models.Model):
    listing = models.ForeignKey(AuctionsListing,on_delete=models.CASCADE,related_name="bids")
    bidder = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.title} by {self.bidder.username}"
    
class Comment(models.Model):
    listing = models.ForeignKey(AuctionsListing,on_delete=models.CASCADE,related_name="comments")
    commenter = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.title} by {self.commenter.username}"
    
class Watchlist(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="watchlist")
    listings = models.ManyToManyField(AuctionsListing)

    def add_watchlist(self,listing):
        self.listings.add(listing)

    def remove_watchlist(self,listing):
        self.listings.remove(listing)

    def __str__(self):
        return f"{self.user.username}'s watchlist"