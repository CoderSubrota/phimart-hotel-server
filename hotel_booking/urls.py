from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hotel_booking.views import api_root 
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Schema view configuration
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api-root'), 
    path('api/accounts/', include(('accounts.urls', 'accounts'), namespace='accounts-root')),
    path('api/hotels/', include(('hotels.urls', 'hotels'), namespace='hotels-root')),
    path('api/bookings/', include(('bookings.urls', 'bookings'), namespace='bookings-root')),
    path('api/dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard-root')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    