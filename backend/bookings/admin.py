from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'start_datetime', 'end_datetime', 'payment_method', 'payment_status', 'user', 'guest_email']
    list_filter = ['room', 'payment_method', 'payment_status']
    search_fields = ['user__email', 'guest_email']
    date_hierarchy = 'start_datetime'
