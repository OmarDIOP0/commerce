from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing",views.create_listing, name="create_listing"),
    path("listing/<str:listing_id>", views.listing,name="listing"),
    path("watchlist",views.watchlist,name="watchlist"),
    path("add_watchlist/<str:listing_id>",views.add_watchlist,name="add_watchlist"),
    path("remove_watchlist/<str:listing_id>",views.remove_watchlist,name="remove_watchlist"),
    path("place_bid/<str:listing_id>",views.place_bid,name="place_bid"),
    path("close_auction/<str:listing_id>",views.close_auction,name="close_auction"),
    path("categories",views.categories,name="categories"),
    path("category_detail/<str:category_id>",views.category_detail,name="category_detail"),
    path("inactive_listing",views.inactive_listing,name="inactive_listing"),
    path("inactive_listing_detail/<str:listing_id>",views.inactive_listing_detail,name="inactive_listing_detail"),
]
