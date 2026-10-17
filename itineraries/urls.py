from django.urls import path
from . import views

app_name = 'itineraries'

urlpatterns = [
    path('', views.itinerary_list, name='list'),
    path('<slug:slug>/', views.itinerary_detail, name='detail'),
]