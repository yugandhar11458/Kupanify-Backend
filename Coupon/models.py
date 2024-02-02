from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatMessage(models.Model):
    sender = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='receiver')
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

class Coupon(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.CharField(max_length=255)
    companyName = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    isAvailed = models.BooleanField(default=False)
    validityDate = models.DateField()
    directUpload = models.BooleanField(default=True)
    couponCode = models.CharField(max_length=255)
    screenshots = models.ImageField(upload_to='coupon_screenshots/', null=True, blank=True)
    
class UserProfile(models.Model):
    userId = models.CharField(max_length=255, primary_key=True)
    userName = models.CharField(max_length=255)
    userImage = models.CharField(max_length=255, null=True, blank=True)
    availedCoupons = models.ManyToManyField(Coupon, related_name='availed_coupons', blank=True)
    uploadedCoupons = models.ManyToManyField(Coupon, related_name='uploaded_coupons', blank=True)
    chat_messages = models.ManyToManyField(ChatMessage, related_name='chat_messages', blank=True)
