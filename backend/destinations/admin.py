from django.contrib import admin

from .models import Country, Destination, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'order']
    list_filter = ['region']


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_featured', 'created_at']
    list_filter = ['country__region', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
