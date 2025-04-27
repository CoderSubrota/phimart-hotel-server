from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,AllowAny
from bookings.models import Booking
from django.db.models import Count, Sum
from hotels.models import Hotel
from accounts.models import User
from django.utils.timezone import now, timedelta

class DashboardStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        today = now()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)

        bookings_week = Booking.objects.filter(created__gte=last_week).count()
        bookings_month = Booking.objects.filter(created__gte=last_month).count()
        top_hotels = Hotel.objects.annotate(book_count=Count('booking')).order_by('-book_count')[:5]
        top_users = User.objects.annotate(total=Count('booking')).order_by('-total')[:5]
        sell_current = Booking.objects.filter(created__month=today.month).aggregate(Sum('amount'))
        sell_prev = Booking.objects.filter(created__month=(today.month - 1)).aggregate(Sum('amount'))

        return Response({
            'bookings_week': bookings_week,
            'bookings_month': bookings_month,
            'top_hotels': [h.name for h in top_hotels],
            'top_users': [u.username for u in top_users],
            'sell_current_month': sell_current['amount__sum'] or 0,
            'sell_previous_month': sell_prev['amount__sum'] or 0,
        })
