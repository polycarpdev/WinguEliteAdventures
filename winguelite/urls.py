from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap

sitemaps = {'pages': StaticViewSitemap}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('destinations/', include('destinations.urls')),
    path('itineraries/', include('itineraries.urls')),
    path('gallery/', include('gallery.urls')),
    path('blog/', include('blog.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('bookings/', include('bookings.urls')),
    path('contact/', include('contact.urls')),
    path('cockpit/', include('cockpit.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)