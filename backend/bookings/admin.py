from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'destination', 'start_date', 'status', 'created_at']
    list_filter = ['status', 'accommodation_preference', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'