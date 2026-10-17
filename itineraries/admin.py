from django.contrib import admin
from .models import Itinerary, ItineraryDay

class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 1

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'duration_days', 'price_from', 'is_featured']
    list_filter = ['destination', 'difficulty', 'is_featured']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ItineraryDayInline]