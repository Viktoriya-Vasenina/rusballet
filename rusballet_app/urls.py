from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/groups/', views.api_groups, name='api_groups'),
    path('api/schedule/', views.api_schedule, name='api_schedule'),
    path('api/booking/create/', views.api_create_booking, name='api_create_booking'),
]