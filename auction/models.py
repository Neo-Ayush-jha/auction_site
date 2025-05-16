from django.db import models
from django.conf import settings  # ✅ this is needed to reference the custom user model

# ------------------------------
# Listing, Bid, Watchlist Models
# ------------------------------
class Listing(models.Model):
    CONDITION_CHOICES = [
        ("New", "New"),
        ("Used", "Used"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=100, null=True, blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, null=True, blank=True)
    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    # Image fields - to match 'public_id' and 'url'
    image_public_id = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.ImageField(upload_to="photo/", null=True, blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    # Commission flag
    commission_calculated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=150, null=True, blank=True)
    profile_image = models.ImageField(upload_to="photo/", null=True, blank=True)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 🔁 FIXED
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

# ------------------------------
# Custom User Model
# ------------------------------

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    
    profile_image_public_id = models.CharField(max_length=255, blank=True, null=True)
    profile_image_url = models.ImageField(upload_to="photo/", null=True, blank=True)

    # Payment Methods
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_account_name = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)

    easypaisa_account_number = models.CharField(max_length=20, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=[("Auctioneer", "Auctioneer"), ("Bidder", "Bidder"), ("Super Admin", "Super Admin")],
        default="Bidder"
    )

    unpaid_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    auctions_won = models.PositiveIntegerField(default=0)
    money_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username



class CommissionProof(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    proof = models.ImageField(upload_to='commission_proofs/')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount}"