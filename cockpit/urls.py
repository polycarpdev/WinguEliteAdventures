from django.urls import path
from . import views

app_name = 'cockpit'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
]