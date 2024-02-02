from rest_framework import serializers
from .models import Coupon, UserProfile, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    couponCode = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Coupon
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    availedCoupons = CouponSerializer(many=True, read_only=True)
    uploadedCoupons = CouponSerializer(many=True, read_only=True)
    chat_messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

