from .models import Watchlist
from django import template

register = template.Library()
def count_watchlist(request):
    if request.user.is_authenticated:
        watchlist_items = Watchlist.objects.filter(user=request.user)
        count = sum(item.listings.count() for item in watchlist_items)
    else:
        count = 0
    return {'count': count}