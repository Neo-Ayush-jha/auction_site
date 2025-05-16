from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Listing, Bid, Watchlist

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id', 'username', 'email', 'role', 'phone', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'role']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'address', 'phone',
                'profile_image_public_id', 'profile_image_url',
                'bank_account_number', 'bank_account_name', 'bank_name',
                'easypaisa_account_number', 'paypal_email',
                'role', 'unpaid_commission', 'auctions_won', 'money_spent'
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': (
                'address', 'phone',
                'profile_image_public_id', 'profile_image_url',
                'bank_account_number', 'bank_account_name', 'bank_name',
                'easypaisa_account_number', 'paypal_email',
                'role', 'unpaid_commission', 'auctions_won', 'money_spent'
            ),
        }),
    )


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner', 'starting_bid', 'current_bid', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'owner__username']
    ordering = ['-created_at']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'listing', 'bid_amount', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'listing__title']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'listing']
    search_fields = ['user__username', 'listing__title']
