from django.contrib import admin
from accounts.models import User
from bookings.models import Booking
from hotels.models import Hotel

admin.site.register(User)
admin.site.register(Booking)
admin.site.register(Hotel)



