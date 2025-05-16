from .models import *
from .serializers import *
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated




from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Listing
from .serializers import ListingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        # ⛔ Block creation if user has unpaid commission
        if request.user.unpaid_commission > 0:
            return Response({
                "error": "You cannot create a new listing until your unpaid commission is cleared."
            }, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_auctions(request):
    user = request.user
    listings = Listing.objects.filter(owner=user)
    serializer = ListingSerializer(listings, many=True, context={'request': request})
    return Response({"my_auctions": serializer.data}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllowAny])  # Or use IsAuthenticated if needed
def get_auction_details_with_bidders(request, id):
    try:
        auction = Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        return Response({"success": False, "message": "Auction not found."}, status=status.HTTP_404_NOT_FOUND)

    bids = Bid.objects.filter(listing=auction).order_by('-bid_amount')
    auction_data = ListingSerializer(auction, context={'request': request}).data
    bidder_data = BidSerializer(bids, many=True, context={'request': request}).data

    return Response({
        "success": True,
        "auctionItem": auction_data,
        "bidders": bidder_data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_user(request):
    if request.method == "POST":
        data = request.data

        try:
            role = data.get("role", "Bidder")  # default to Bidder if role not provided

            # Common required fields
            user = CustomUser.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                address=data.get("address", ""),
                phone=data.get("phone", ""),
                profile_image_public_id=data.get("profile_image_public_id"),
                profile_image_url=data.get("profile_image_url"),
                role=role,
            )

            # Only set bank/easypaisa/paypal info if not a Bidder
            if role != "Bidder":
                user.bank_account_number = data.get("bank_account_number", "")
                user.bank_account_name = data.get("bank_account_name", "")
                user.bank_name = data.get("bank_name", "")
                user.easypaisa_account_number = data.get("easypaisa_account_number", "")
                user.paypal_email = data.get("paypal_email", "")

            # Assign group if Auctioneer
            if role == "Auctioneer":
                auctioneer_group, created = Group.objects.get_or_create(name="Auctioneer")
                user.groups.set([auctioneer_group])

            user.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({"error": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    print(user.id)
    profile_data = {
        'id':user.id,
        'userName': user.username,
        'email': user.email,
        'phone': getattr(user, 'phone', ''),
        'address': getattr(user, 'address', ''),
        'role': getattr(user, 'role', ''),
        "profileImage": request.build_absolute_uri(user.profile_image_url.url) if user.profile_image_url else "",
        'createdAt': user.date_joined.strftime('%Y-%m-%d') if user.date_joined else '',
        'unpaidCommission': getattr(user, 'unpaid_commission', 0),
        'auctionsWon': getattr(user, 'auctions_won', 0),
        'moneySpent': getattr(user, 'money_spent', 0.0),
        'bankAccountNumber': getattr(user, 'bank_account_number', ''),
        'bankAccountName': getattr(user, 'bank_account_name', ''),
        'bankName': getattr(user, 'bank_name', ''),
        'easypaisaAccountNumber': getattr(user, 'easypaisa_account_number', ''),
        'paypalEmail': getattr(user, 'paypal_email', ''),
    }

    return Response({"user": profile_data}, status=status.HTTP_200_OK)




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logged out successfully. Please remove token from client."}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllowAny])  # Use IsAuthenticated if you want to restrict
def leaderboard(request):
    users = CustomUser.objects.filter(money_spent__gt=0).order_by('-money_spent')

    leaderboard_data = [
        {
            "username": user.username,
            "moneySpent": user.money_spent,
            "auctionsWon": user.auctions_won,
            "profileImage": request.build_absolute_uri(user.profile_image_url.url) if user.profile_image_url else "",
        }
        for user in users
    ]

    return Response({
        "success": True,
        "leaderboard": leaderboard_data
    }, status=200)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Listing, Bid, CustomUser

from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail
from .models import Listing, Bid, CustomUser
from decimal import Decimal

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_all_expired_auctions(request):
    now = timezone.now()
    ended_auctions = []
    skipped_auctions = []

    expired_listings = Listing.objects.filter(is_active=True, end_time__lte=now)

    for listing in expired_listings:
        try:
            bids = Bid.objects.filter(listing=listing).order_by('-bid_amount')

            if not bids.exists():
                listing.is_active = False
                listing.commission_calculated = True
                listing.save()
                skipped_auctions.append({
                    "listing_id": listing.id,
                    "title": listing.title,
                    "message": "No bids placed."
                })
                continue

            highest_bid = bids.first()
            winner = highest_bid.user
            bid_amount = highest_bid.bid_amount

            # Update winner stats
            winner.money_spent += bid_amount
            winner.auctions_won += 1
            winner.unpaid_commission += bid_amount * Decimal('0.05')
            winner.save()

            # Update listing
            listing.is_active = False
            listing.commission_calculated = True
            listing.save()

            # Send winner email
            send_mail(
                subject="🎉 Congratulations! You've won the auction",
                message=(
                    f"Dear {winner.username},\n\n"
                    f"You've won the auction '{listing.title}' with a bid of ${bid_amount}.\n"
                    f"Please be prepared to make the payment and upload proof.\n\n"
                    f"Your commission (5%) is: ${bid_amount * Decimal('0.05')}\n"
                    f"Total Amount: ${bid_amount + (bid_amount * Decimal('0.05'))}\n\n"
                    "Thank you for participating in our auction!\n"
                    "- Auction Platform Team"
                ),
                from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
                recipient_list=[winner.email],
                fail_silently=False,
            )

            ended_auctions.append({
                "listing_id": listing.id,
                "title": listing.title,
                "winner": winner.username,
                "bid_amount": str(bid_amount)
            })

        except Exception as e:
            skipped_auctions.append({
                "listing_id": listing.id,
                "title": listing.title,
                "error": str(e)
            })

    return Response({
        "success": True,
        "ended_auctions": ended_auctions,
        "skipped_auctions": skipped_auctions,
    }, status=200)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Listing, Bid
from decimal import Decimal

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bid(request, listing_id):
    try:
        user = request.user
        data = request.data
        amount = data.get("amount")

        if not amount:
            return Response({"error": "Bid amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except:
            return Response({"error": "Invalid bid amount."}, status=status.HTTP_400_BAD_REQUEST)

        listing = Listing.objects.get(id=listing_id)

        if amount <= listing.current_bid:
            return Response({"error": "Bid amount must be greater than current bid."}, status=status.HTTP_400_BAD_REQUEST)

        if amount < listing.starting_bid:
            return Response({"error": "Bid amount must be greater than starting bid."}, status=status.HTTP_400_BAD_REQUEST)

        bid = Bid.objects.create(
            listing=listing,
            user=user,
            user_name=user.username,
            profile_image=user.profile_image_url,
            bid_amount=amount
        )

        listing.current_bid = amount
        listing.save()

        return Response({"message": "Bid placed successfully."}, status=status.HTTP_201_CREATED)

    except Listing.DoesNotExist:
        return Response({"error": "Listing not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UploadCommissionProof(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = CommissionProofSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            # 📧 Send confirmation email after proof is saved
            send_mail(
                subject="🧾 Payment Proof Received",
                message=(
                    f"Dear {request.user.username},\n\n"
                    "Thanks for submitting your commission payment proof. "
                    "We will review and verify it within 24 hours.\n\n"
                    "Regards,\nAuction Platform Team"
                ),
                from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            return Response({
                "success": True,
                "message": "Proof uploaded successfully. It will be reviewed within 24 hours.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests

@api_view(['POST'])
def contact_us(request):
    try:
        data = request.data

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        subject = data.get("subject")
        message = data.get("message")

        mailtrap_url = "https://sandbox.api.mailtrap.io/api/send/3695683"

        headers = {
            "Authorization": "Bearer 80df0524c8626d89c794c4e61acd7364",  # Replace with actual token
            "Content-Type": "application/json"
        }

        payload = {
            "from": {
                "email": "sandbox@mailtrap.io",  # Or a verified sender email
                "name": "Auction Contact"
            },
            "to": [
                {
                    "email": "gaqapuliqo@mailinator.com",  # 👈 Your target recipient
                    "name": "Admin"
                }
            ],
            "subject": f"New Contact Message: {subject}",
            "text": (
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"Subject: {subject}\n\n"
                f"Message:\n{message}"
            ),
            "category": "contact_form"
        }

        response = requests.post(mailtrap_url, json=payload, headers=headers)

        if response.status_code in [200, 202]:
            return Response({"message": "Message sent successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to send email.",
                "details": response.json()
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
