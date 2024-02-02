from django.urls import path
from .views import (
    coupon_list_create,
    coupon_detail,
    user_profile_list,
    user_profile_detail,
    chat_messages,
    user_chat_list,
    avail_coupon,
    disavail_coupon,
    latest_coupons
)

urlpatterns = [
    path('coupons/', coupon_list_create, name='coupon-list-create'),
    path('coupons/<int:id>/', coupon_detail, name='coupon-detail'),
    path('coupons/latest/', latest_coupons, name='latest_coupons'),
    path('user-profiles/', user_profile_list, name='user-profile-list'),
    path('user-profile/<str:userId>/', user_profile_detail, name='user-profile-detail'),
    path('chat/messages/<str:user_id>/', user_chat_list, name='user_chat_list'),
    path('chat/messages/<str:user_id>/<str:other_user_id>/', chat_messages, name='chat_messages'),
    path('coupons/<int:id>/avail/<str:user_id>/', avail_coupon, name='avail-coupon'),  
    path('coupons/<int:id>/disavail/<str:user_id>/', disavail_coupon, name='disavail-coupon'),  
]
