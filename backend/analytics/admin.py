from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'path', 'referrer', 'device', 'browser', 'timezone']
    list_filter = ['device', 'browser']
    search_fields = ['path', 'referrer']
