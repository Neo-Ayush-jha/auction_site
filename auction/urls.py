from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bids', BidViewSet)
router.register(r'watchlist', WatchlistViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', register_user, name='register'),
    path('api/me/', get_user_profile, name='get_user_profile'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/my-auctions/', my_auctions, name='my_auctions'),
    path('api/leaderboard/', leaderboard, name='leaderboard'),
    path('api/auction/<int:id>/', get_auction_details_with_bidders, name='auction-details'),
    path('api/bid/place/<int:listing_id>/', place_bid, name='place-bid'),
    path('api/auction/end-all/', end_all_expired_auctions, name='end-all-expired-auctions'),
    path('api/commission/proof/', UploadCommissionProof.as_view(), name='upload-commission-proof'),
    path("api/contact/", contact_us, name="contact_us"),

]
