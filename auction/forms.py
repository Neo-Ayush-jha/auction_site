from django import forms
from .models import Listing, Bid

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']
