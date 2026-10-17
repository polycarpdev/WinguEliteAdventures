from django.urls import path

from . import views

urlpatterns = [
    path('bookings/', views.booking, name='api-booking'),
    path('contact/', views.contact, name='api-contact'),
    path('health/', views.health, name='api-health'),
]
