from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import StaffAuthenticationForm
from .views import content, enquiries, overview, users

app_name = 'cockpit'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='cockpit/login.html', authentication_form=StaffAuthenticationForm,
        redirect_authenticated_user=True, next_page=reverse_lazy('cockpit:dashboard')), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('cockpit:login')), name='logout'),

    path('', overview.dashboard, name='dashboard'),
    path('analytics/', overview.analytics, name='analytics'),
    path('reports/', overview.reports, name='reports'),

    path('bookings/', enquiries.booking_list, name='booking_list'),
    path('bookings/export.csv', overview.bookings_csv, name='bookings_csv'),
    path('bookings/<int:pk>/', enquiries.booking_detail, name='booking_detail'),
    path('messages/', enquiries.message_list, name='message_list'),
    path('messages/<int:pk>/', enquiries.message_detail, name='message_detail'),
    path('contacts/', enquiries.message_list, name='contact_list'),
    path('contacts/<int:pk>/', enquiries.message_detail, name='contact_detail'),

    path('account/', users.account, name='account'),
    path('users/', users.user_list, name='users'),
    path('users/new/', users.user_edit, name='user_add'),
    path('users/<int:pk>/', users.user_edit, name='user_edit'),

    path('content/<slug:key>/', content.content_list, name='content_list'),
    path('content/<slug:key>/new/', content.content_edit, name='content_add'),
    path('content/<slug:key>/<int:pk>/', content.content_edit, name='content_edit'),
    path('content/<slug:key>/<int:pk>/delete/', content.content_delete, name='content_delete'),
]
