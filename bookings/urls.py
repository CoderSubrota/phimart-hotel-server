from django.urls import path
from .views import BookHotelAPIView

urlpatterns = [
    path('', BookHotelAPIView.as_view()),
]

