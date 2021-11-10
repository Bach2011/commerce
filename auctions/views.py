from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import Form
from .models import Bids, Comment, User, Listing, Watchlist
from datetime import datetime
from django.contrib.auth.decorators import login_required
class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={"name":"comment", "placeholder":"Comment something!","rows":"3"}), label="")

class BidForm(forms.Form):
    Bid = forms.IntegerField(label="", widget=forms.NumberInput(attrs={"placeholder":"Bid", "name":"bid"}))
class NewListingForm(forms.Form):
    categories = Listing.categories
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea, max_length=200)
    starting_bid = forms.IntegerField()
    image_url = forms.CharField(required=False)
    category = forms.ChoiceField(choices=categories)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
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
@login_required
def listing(request, listing_id):
    bid = str(request.POST.get('Bid'))
    close_listing = request.POST.get('close')
    user = request.user.username
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST" and bid == "None" and close_listing == None:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            Comment.objects.create(comment=comment, user=user, listing_id=listing_id)
    if request.method == "POST" and bid != "None":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data['Bid']
            current_bid = Bids.objects.get(listing_id=listing_id)
            if int(bid) > int(str(current_bid)):
                current_bid.bid = bid
                current_bid.username = user
                current_bid.save()
            else: 
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comments": Comment.objects.filter(listing_id=listing_id),
                    "bid_form": BidForm(),
                    "comment_form": CommentForm(),
                    "bid": Bids.objects.get(listing_id=listing_id),
                    "message": "You need to bid larger than the current bid"
                })
    if request.method == "POST" and close_listing != None:
        listing.active = False
        Watchlist.objects.get(listing_id=listing_id, user=user).delete()
        listing.save()
        
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": Comment.objects.filter(listing_id=listing_id),
        "bid_form": BidForm(),
        "comment_form": CommentForm(),
        "bid": Bids.objects.get(listing_id=listing_id)
    })
@login_required
def new(request):
    now = datetime.now()
    today = datetime.today()
    current_time = today.strftime("%d %m, %Y") + now.strftime(" %H:%M:%S")
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            try:
                listing_id = Listing.objects.last().id + 1
            except AttributeError:
                listing_id = 1
            Bids.objects.create(listing_id=int(listing_id), bid=starting_bid)
            bid = Bids.objects.last()
            listing = Listing(title=title, description=description, current_bid=bid, image_url=image_url, category=category, time=current_time, user=request.user.username)
            listing.save()
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
@login_required
def watchlist(request):
    user = request.user.username
    delete_listing = request.POST.get('delete')
    title = request.POST.get('watchlist')
    if request.method == "POST" and title != None:
        listing = Listing.objects.get(title=title)
        try:
            watchlist = Watchlist.objects.get(title=title, user=user)
        except:
            Watchlist.objects.create(title=listing.title, user=user, listing_id=listing.id, listing_image=listing.image_url)
        return HttpResponseRedirect(reverse('watchlist'))
    if request.method == "POST" and delete_listing != None:
        Watchlist.objects.get(title=delete_listing, user=user).delete()
    return render(request, "auctions/watchlist.html", {
        "listings": Watchlist.objects.filter(user=user),
    })
    