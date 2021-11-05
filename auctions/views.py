from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms.widgets import Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import Form
from .models import Bids, Comment, User, Listing, Watchlist
from datetime import datetime

class NewListingForm(forms.Form):
    categories = Listing.categories
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea, max_length=200)
    starting_bid = forms.IntegerField()
    image_url = forms.CharField(required=False)
    category = forms.ChoiceField(choices=categories)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "Watchlist": Watchlist.objects.filter(user=request.user.username)
    })


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
def listing(request, listing_id):
    bid = str(request.POST.get('bid'))
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        if len(bid) > 0:
            Bids.objects.get(listing_id=listing_id).bid = bid
        else:
            return render(request,"auctions/listing.html", {
                "listing": listing
            })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": Comment.objects.filter(listing_id=listing_id)
    })

def new(request):
    now = datetime.now()
    today = datetime.today()
    current_time = today.strftime("%d %m, %Y") + now.strftime(" %S:%M:%H")
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            Bids.objects.create(listing_id=int(Listing.objects.last().id)+1, bid=starting_bid)
            Listing.objects.create(title=title, description=description,current_bid=starting_bid, image_url=image_url, category=category, user=request.user.username, time=current_time)
            return HttpResponseRedirect(reverse("listing", args=str(Listing.objects.last().id)))
    return render(request, "auctions/new.html", {
        "form": NewListingForm
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.categories
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category=category)
    })

def watchlist(request):
    if request.method == "POST":
        title = request.POST.get('watchlist')
        listing = Listing.objects.get(title=title)
        Watchlist.objects.create(title=listing.title, user=request.user.username, listing_id=listing.id, listing_image=listing.image_url)
    return render(request, "auctions/watchlist.html", {
        "listings": Watchlist.objects.filter(user=request.user.username),
    })