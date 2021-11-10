from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class Bids(models.Model):
    username = models.CharField(max_length=64, default="admin")
    bid = models.IntegerField()
    listing_id = models.IntegerField()
    def __str__(self):
        return f"{self.bid}"

class Listing(models.Model):
    categories = [
        ("movies", "movies"),
        ("antique", "antique"),
        ("magical", "magical"),
        ("rare item", "rare item"),
        ("fashion", "fashion"),
        ("toys", "toys"),
        ("electronics", "electronics")
    ]

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    current_bid = models.ForeignKey(Bids, on_delete=CASCADE, related_name="bids", default=10000)
    image_url = models.CharField(max_length=400, blank=True)
    category = models.CharField(choices=categories, max_length=1000, default="movies")
    user = models.CharField(max_length=20)  
    time = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.id}: {self.title}"
class Watchlist(models.Model):
    title = models.CharField(max_length=90, default="listing")
    user = models.CharField(max_length=20, default="admin")
    listing_id = models.IntegerField(default=1)
    listing_image = models.CharField(max_length=1000, default="Type something!")
    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    user = models.CharField(max_length=64, default="admin")
    listing_id = models.IntegerField()
    comment = models.CharField(max_length=1000, default="Type something!")
    def __str__(self):
        return f"{self.user} : {self.comment}"