from rest_framework.routers import DefaultRouter
from hotels.views import HotelViewSet
from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from hotels.views import ReviewViewSet,HotelReviewCreateView,HotelImageUploadView,CreatePaymentIntentView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Hotel Booking API",
      default_version='v1',
      description="API documentation for the Hotel Booking system",
      contact=openapi.Contact(email="contact@hotel.local"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r'', HotelViewSet)

hotel_router = NestedDefaultRouter(router, r'', lookup='hotel')
hotel_router.register(r'reviews', ReviewViewSet, basename='hotel-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(hotel_router.urls)),
    path('<int:hotel_id>/payment/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('<int:hotel_id>/reviews/', HotelReviewCreateView.as_view(), name='hotel-review'),
    path('<int:hotel_id>/images/', HotelImageUploadView.as_view(), name='hotel-image-upload'),
   
]