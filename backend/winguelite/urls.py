from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

# The public site is static HTML built by Astro (see web/). Django only serves
# the cockpit (staff), the form/analytics API and (in development) media files.
# Django's built-in /admin/ is deliberately not routed: everything staff need
# lives in the cockpit, which has login throttling and a smaller surface.
urlpatterns = [
    path('cockpit/', include('cockpit.urls')),
    path('api/', include('api.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'api.views.not_found'
