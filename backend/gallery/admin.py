from django.contrib import admin
from .models import GalleryAlbum, GalleryImage

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3

@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GalleryImageInline]