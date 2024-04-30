from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,get_object_or_404,get_list_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User,AuctionsListing,Category,Bid,Comment,Watchlist
from .utils import count_watchlist
from .forms import BidForm,CommentForm
from django.contrib import messages
from django.db.models import Max


def index(request):
    message = request.GET.get('message','')
    listings = AuctionsListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html",{'message':message, 'listings':listings })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description","")
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST.get("image_url","")
        creator = request.user
        category_name = request.POST.get("category","")
        if category_name:
            category,created = Category.objects.get_or_create(name=category_name)
        else:
            category = None
        try:
            AuctionsListing.objects.create(title=title,description=description,starting_bid=starting_bid,current_bid=starting_bid,image_url=image_url, category=category,creator=creator)
        except IntegrityError as e:
            return render(request, "auctions/create_listing.html", {
                "message": "Could not create listing" + str(e)
            })
        return HttpResponseRedirect(reverse("index")+"?message = Listing+created+successfully")
    else:
        return render(request, "auctions/create_listing.html")
    
def listing(request,listing_id):
    listing = AuctionsListing.objects.get(pk=listing_id)
    form_bid = BidForm()
    messages = request.GET.get('messages')
    user = request.user
    is_winner = listing.is_winner(user) if user.is_authenticated else False
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            Comment.objects.create(listing=listing,commenter=request.user,content=content)
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        form = CommentForm()
    comments = Comment.objects.filter(listing=listing)
    return render(request, "auctions/listing.html", {'listing':listing,'form_bid' : form_bid,'form':form,'message':messages,'is_winner':is_winner,'comments':comments})


@login_required
def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(user=user).first()
    return render(request, "auctions/watchlist.html", {'watchlist':watchlist})

@login_required
def add_watchlist(request, listing_id):
    listing = AuctionsListing.objects.get(pk=listing_id)
    user = request.user
    watchlist,create = Watchlist.objects.get_or_create(user=user)
    watchlist.add_watchlist(listing)
    return HttpResponseRedirect(reverse('watchlist'))

@login_required
def remove_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionsListing,pk=listing_id)
    user = request.user
    watchlist = get_object_or_404(Watchlist,user=user)
    watchlist.remove_watchlist(listing)
    return HttpResponseRedirect(reverse('watchlist'))

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(AuctionsListing,pk=listing_id)
    if request.method == 'POST':
        form =BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']
            if bid_amount >= listing.starting_bid and ( not listing.current_bid or bid_amount > listing.current_bid):
                listing.current_bid = bid_amount
                listing.save()
                try:
                    Bid.objects.create(listing=listing, bidder=request.user, amount=bid_amount)
                    messages.success(request,'Your bid has been placed successfully')
                    return HttpResponseRedirect(reverse('listing', args=[listing_id])+"?message = your+bit+has+been+placed+successfully")
                except IntegrityError as e:
                    messages.error(request,'Could not place bid'+ str(e))
                    return HttpResponseRedirect(reverse("listing",args=[listing_id])+"?message = could+not+place+bid")
            else:
                messages.error(request,'Your bid must be higher than the current bid')
                return HttpResponseRedirect(reverse("listing",args=[listing_id])+"?message = your+bid+must+be+higher+than+the+current+bid")
    else:
        form = BidForm()

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))
@login_required
def close_auction(request,listing_id):
    listing = AuctionsListing.objects.get(pk=listing_id)
    if request.user == listing.creator:
        if not listing.is_active:
            messages.error(request,'Bid already closed')
        else:
            bids = Bid.objects.filter(listing=listing)
            if bids.exists():
                winning_bid = bids.aggregate(Max('amount'))['amount__max']
                winning_bidder = bids.filter(amount=winning_bid).first().bidder
                listing.winner = winning_bidder
            listing.is_active = False
            listing.save()
            messages.success(request,f"Bid closed successfully. The winner is {winning_bidder.username}")
    else:
        messages.error(request,'You are not the creator of this listing')
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))
@login_required
def categories(request):
    categories = Category.objects.exclude(name='')
    number = categories.count()
    return render(request, "auctions/categories.html", {'categories':categories, 'number':number})
@login_required
def category_detail(request,category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = AuctionsListing.objects.filter(category=category,is_active=True)
    return render(request, "auctions/category_detail.html",{'category':category,'listings':listings})

@login_required
def inactive_listing(request):
    listings = AuctionsListing.objects.filter(is_active=False)
    return render(request, "auctions/inactive_listing.html",{'listings':listings })

@login_required
def inactive_listing_detail(request,listing_id):
    listing = AuctionsListing.objects.get(pk=listing_id , is_active=False)
    user = request.user
    is_winner = listing.is_winner(user) if user.is_authenticated else False
    return render(request, "auctions/inactive_listing_detail.html", {'listing':listing,'is_winner':is_winner})







