from django.urls import path

from analytics.views import hit

from . import views

urlpatterns = [
    path('bookings/', views.booking, name='api-booking'),
    path('contact/', views.contact, name='api-contact'),
    path('hit/', hit, name='api-hit'),
    path('health/', views.health, name='api-health'),
]
