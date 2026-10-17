from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_index, name='index'),
    path('album/<slug:slug>/', views.album_detail, name='album_detail'),
]