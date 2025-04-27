from rest_framework import viewsets, permissions
from hotels.models import Hotel, Review
from hotels.serializers import HotelSerializer, ReviewSerializer,HotelImageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse
from django.views import View
import stripe
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
import json

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.AllowAny]
    
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]  # Allow access to everyone (you may replace with secure permissions)
    
    def get_queryset(self):
        # Ensure 'hotel_pk' exists in kwargs, or handle gracefully
        hotel_pk = self.kwargs.get('hotel_pk')
        if not hotel_pk:
            return Review.objects.none()  # Return empty queryset if no hotel_pk
        return Review.objects.filter(hotel_id=hotel_pk)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, hotel_id=self.kwargs['hotel_pk'])

@api_view(['GET'])
def hotels_root(request):
    return Response({'message': 'Welcome to the Hotels API'})

class HotelReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny] 
    
    def post(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prevent duplicate reviews
        if Review.objects.filter(user=request.user, hotel=hotel).exists():
            return Response({'error': 'You have already reviewed this hotel.'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['hotel'] = hotel.id
        serializer = self.get_serializer(data=data)
        
        # Handle validation errors
        if serializer.is_valid():
            serializer.save(user=request.user, hotel=hotel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HotelImageUploadView(generics.CreateAPIView):
    serializer_class = HotelImageSerializer
    permission_classes = [permissions.AllowAny]  

    def post(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hotel'] = hotel.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(hotel=hotel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Payment view 
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@method_decorator(csrf_exempt, name='dispatch') 
class CreatePaymentIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            amount = int(data.get('amount', 0))  
            
            if amount <= 0:
                raise ValueError("Invalid amount provided")
            
            # Create a payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency='usd',
            )
            return JsonResponse({
                'clientSecret': payment_intent['client_secret'],
                'transactionId': payment_intent['id'], 
                'amount': amount
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        