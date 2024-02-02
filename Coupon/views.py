
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Coupon, UserProfile, ChatMessage
from .serializers import CouponSerializer, UserProfileSerializer, ChatMessageSerializer
from datetime import date
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

# User views
@api_view(['GET', 'POST'])
def user_profile_list(request):
    """
    GET: Retrieve a list of user profiles.
    POST: Create or update a user profile.
    """
    if request.method == 'GET':
        # Retrieve all user profiles
        user_profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(user_profiles, many=True)
        # Format and return the response data
        response_data = [{'userId': str(profile['userId']),
                          'userName': profile['userName'],
                          'userImage': profile['userImage']} for profile in serializer.data]
        return Response(response_data)

    elif request.method == 'POST':
        # Check if the user profile already exists
        existing_profile = UserProfile.objects.filter(userId=request.data.get('userId')).first()

        if existing_profile:
            serializer = UserProfileSerializer(existing_profile, data=request.data)
        else:
            serializer = UserProfileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'User is added/updated successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def user_profile_detail(request, userId):
    """
    GET: Retrieve a user profile.
    PUT/PATCH: Update a user profile.
    DELETE: Delete a user profile.
    """
    user_profile = get_object_or_404(UserProfile, userId=userId)

    # Delete expired coupons before processing the request
    delete_expired_coupons()

    if request.method == 'GET':
        serializer = UserProfileSerializer(user_profile)
        response_data = {'userId': str(serializer.data['userId']),
                         'userName': serializer.data['userName'],
                         'availedCoupons': serializer.data['availedCoupons'],
                         'uploadedCoupons': serializer.data['uploadedCoupons'],
                         'userImage': serializer.data['userImage']}
        return Response(response_data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Function to delete expired coupons
def delete_expired_coupons():
    """
    Delete expired coupons from the database.
    """
    expired_coupons = Coupon.objects.filter(validityDate__lt=date.today())
    expired_coupons.delete()

# Coupon Views
@api_view(['GET', 'POST'])
def coupon_list_create(request):
    """
    GET: Retrieve a list of coupons based on query parameters.
    POST: Create a new coupon.
    """
    # Call function to delete expired coupons
    delete_expired_coupons()

    if request.method == 'GET':
        # Extract query parameters from the request
        company_name = request.GET.get('companyName', None)
        category = request.GET.get('category', None)
        userId = request.GET.get('userId', None)

        # Build the filter conditions
        filters = Q()
        if company_name:
            filters &= Q(companyName__icontains=company_name)
        if category:
            filters &= Q(category=category)

        # Exclude coupons uploaded by the current user
        if userId:
            filters &= ~Q(userId=userId)

        # Apply the filters
        coupons = Coupon.objects.filter(filters, isAvailed=False)

        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CouponSerializer(data=request.data)
        try:
            if serializer.is_valid():
                # Handle default values when directUpload is "false"
                if serializer.validated_data.get('directUpload') == 'false':
                    serializer.validated_data['couponCode'] = '' if not serializer.validated_data.get(
                        'couponCode') else serializer.validated_data['couponCode']
                    serializer.validated_data['screenshots'] = None if not serializer.validated_data.get(
                        'screenshots') else serializer.validated_data['screenshots']

                print("Serializer validated data:", serializer.validated_data)

                coupon = serializer.save()
                user_profile = UserProfile.objects.get(userId=coupon.userId)
                user_profile.uploadedCoupons.add(coupon)

                print("Coupon saved successfully")

                return Response(serializer.data, status=201)
            else:
                raise ValidationError(serializer.errors)
        except ValidationError as e:
            print("Validation error:", e.detail)
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception:", str(e))
            return Response({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def coupon_detail(request, id):
    """
    GET: Retrieve a coupon.
    PUT/PATCH: Update a coupon.
    DELETE: Delete a coupon.
    """
    coupon = get_object_or_404(Coupon, id=id)

    if request.method == 'GET':
        serializer = CouponSerializer(coupon)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = CouponSerializer(coupon, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        coupon.delete()
        return Response(status=204)

@api_view(['GET'])
@permission_classes([AllowAny])
def latest_coupons(request):
    """
    GET: Retrieve the latest coupons.
    """
    limit = int(request.GET.get('limit', 20))  # Default to 20 if limit is not provided
    userId = request.GET.get('userId', None)  # Get the user ID from the request

    try:
        # Get the latest coupons that are not availed and exclude those uploaded by the current user
        coupons = Coupon.objects.filter(~Q(userId=userId) if userId else Q(), isAvailed=False).order_by('-id')[:limit]

        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print("Error fetching coupons:", str(e))
        return Response({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def avail_coupon(request, id, user_id):
    """
    POST: Avail a coupon.
    """
    coupon = get_object_or_404(Coupon, id=id)
    user_profile = get_object_or_404(UserProfile, userId=user_id)

    # Check if the coupon is not already availed
    if coupon.isAvailed:
        return Response({'detail': 'Coupon is already availed'}, status=status.HTTP_400_BAD_REQUEST)

    # Add the coupon to the user's availedCoupons
    user_profile.availedCoupons.add(coupon)

    # Toggle isAvailed to True
    coupon.isAvailed = True
    coupon.save()

    return Response({'detail': 'Coupon added to availed coupons successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def disavail_coupon(request, id, user_id):
    """
    POST: Disavail a coupon.
    """
    coupon = get_object_or_404(Coupon, id=id)
    user_profile = get_object_or_404(UserProfile, userId=user_id)

    # Check if the coupon is already availed
    if not coupon.isAvailed:
        return Response({'detail': 'Coupon is not availed'}, status=status.HTTP_400_BAD_REQUEST)

    # Remove the coupon from the user's availedCoupons
    user_profile.availedCoupons.remove(coupon)

    # Toggle isAvailed to False
    coupon.isAvailed = False
    coupon.save()

    return Response({'detail': 'Coupon removed from availed coupons successfully'}, status=status.HTTP_200_OK)

# Chat views
@api_view(['GET', 'POST'])
def user_chat_list(request, user_id, other_user_id=None):
    """
    GET: Retrieve a list of users with whom the current user has chatted.
    POST: Create a new chat message.
    """
    if request.method == 'GET':
        # Retrieve all user profiles related to the user with ID user_id
        user_profiles = UserProfile.objects.filter(
            chat_messages__sender__userId=user_id
        ).distinct() | UserProfile.objects.filter(
            chat_messages__receiver__userId=user_id
        ).distinct()

        # Exclude the current user's profile
        user_profiles = user_profiles.exclude(userId=user_id)

        # Serialize only the required fields
        serialized_data = []
        for user_profile in user_profiles:
            user_data = {
                'userId': user_profile.userId,
                'userName': user_profile.userName,
                'userImage': user_profile.userImage if user_profile.userImage else None,
            }

            serialized_data.append(user_data)

        return Response(serialized_data)

    elif request.method == 'POST':
        sender_profile = get_object_or_404(UserProfile, userId=user_id)
        receiver_profile = get_object_or_404(UserProfile, userId=other_user_id)
        serializer = ChatMessageSerializer(data=request.data)

        if serializer.is_valid():
            # Create a new chat message
            chat_message = serializer.save(sender=sender_profile, receiver=receiver_profile, timestamp=timezone.now())

            # Update user profiles with the new chat message
            sender_profile.chat_messages.add(chat_message)
            receiver_profile.chat_messages.add(chat_message)

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

@api_view(['GET', 'POST'])
def chat_messages(request, user_id, other_user_id):
    """
    GET: Retrieve chat messages between two users.
    POST: Create a new chat message.
    """
    if request.method == 'GET':
        # Retrieve chat messages between two users
        chat_messages = ChatMessage.objects.filter(
            Q(sender_id=user_id, receiver_id=other_user_id) | Q(sender_id=other_user_id, receiver_id=user_id)
        ).order_by('timestamp')

        # If no messages exist, create an empty message and add it to user profiles
        if not chat_messages.exists():
            sender_profile = get_object_or_404(UserProfile, userId=user_id)
            receiver_profile = get_object_or_404(UserProfile, userId=other_user_id)

            empty_message = ChatMessage.objects.create(
                content='',
                sender=sender_profile,
                receiver=receiver_profile
            )

            # Update user profiles with the new empty message
            sender_profile.chat_messages.add(empty_message)
            receiver_profile.chat_messages.add(empty_message)

            # Update the chat_messages queryset
            chat_messages = ChatMessage.objects.filter(
                Q(sender_id=user_id, receiver_id=other_user_id) | Q(sender_id=other_user_id, receiver_id=user_id)
            ).order_by('timestamp')

        serializer = ChatMessageSerializer(chat_messages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        sender_id = user_id
        receiver_id = other_user_id

        sender_profile = get_object_or_404(UserProfile, userId=sender_id)
        receiver_profile = get_object_or_404(UserProfile, userId=receiver_id)

        request.data['sender'] = sender_id
        request.data['receiver'] = receiver_id

        serializer = ChatMessageSerializer(data=request.data)

        if serializer.is_valid():
            # Create a new chat message
            chat_message = serializer.save(sender=sender_profile, receiver=receiver_profile)

            # Update user profiles with the new chat message
            sender_profile.chat_messages.add(chat_message)
            receiver_profile.chat_messages.add(chat_message)

            return Response(serializer.data, status=201)
        else:
            # Handle default case for content and image
            content = request.data.get('content', '')  # Get content or default to an empty string
            image = request.data.get('image', '')  # Get image or default to None

            # Create a new chat message with default values
            chat_message = ChatMessage.objects.create(
                content=content,
                image=image,
                sender=sender_profile,
                receiver=receiver_profile
            )

            return Response(ChatMessageSerializer(chat_message).data, status=201)

        return Response(serializer.errors, status=400)
