from rest_framework import generics, permissions, status
from rest_framework.response import Response
from bookings.serializers import BookingSerializer
from django.core.mail import send_mail

class BookHotelAPIView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        hotel = serializer.validated_data['hotel']
        amount = serializer.validated_data['amount']
        user = request.user

        if user.balance >= amount:
            user.balance -= amount
            user.save()

            booking = serializer.save(user=user)

            send_mail(
                'Booking Confirmation',
                f'You have successfully booked {hotel.name}.',
                'noreply@hotelbooking.com',
                [user.email],
                fail_silently=True,
            )

            return Response({
                'message': f'Booking successful for {hotel.name}.',
                'booking_id': booking.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Insufficient balance to complete booking.'
            }, status=status.HTTP_400_BAD_REQUEST)
