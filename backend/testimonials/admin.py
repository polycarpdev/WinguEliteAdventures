from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'trip', 'rating', 'date', 'is_featured']
    list_filter = ['rating', 'is_featured', 'date']
    search_fields = ['client_name', 'review']