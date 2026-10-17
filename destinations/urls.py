from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('<str:country_type>/', views.destination_list, name='list'),
    path('detail/<slug:slug>/', views.destination_detail, name='detail'),
]