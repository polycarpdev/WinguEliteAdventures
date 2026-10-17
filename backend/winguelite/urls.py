from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# The public site is static HTML built by Astro (see web/). Django only serves
# the admin, the cockpit, the form API and (in development) media files.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('cockpit/', include('cockpit.urls')),
    path('api/', include('api.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Wingu Elite Adventures'
admin.site.site_title = 'Wingu Elite Admin'
admin.site.index_title = 'Content & bookings'
