from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'

class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            # Add any custom fields if needed
        }

        return data

class BidSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Bid
        fields = ['id', 'user_name', 'profile_image', 'bid_amount', 'timestamp']

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.user.profile_image_url:
            return request.build_absolute_uri(obj.user.profile_image_url.url)
        return ""



class CommissionProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionProof
        fields = ['id', 'proof', 'amount', 'comment']
    
    def validate(self, data):
        user = self.context['request'].user
        if user.unpaid_commission < data['amount']:
            raise serializers.ValidationError(
                f"Amount exceeds unpaid commission balance (₹{user.unpaid_commission})"
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        user.unpaid_commission -= validated_data['amount']
        user.save()
        return CommissionProof.objects.create(user=user, **validated_data)