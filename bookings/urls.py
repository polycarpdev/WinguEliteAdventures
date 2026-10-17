from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_create, name='create'),
    path('success/', views.booking_success, name='success'),
]