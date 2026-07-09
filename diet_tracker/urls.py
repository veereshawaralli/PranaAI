from django.urls import path
from . import views

app_name = 'diet_tracker'

urlpatterns = [
    path('', views.scan_food, name='scan_food'),
    path('result/<int:scan_id>/', views.scan_result, name='scan_result'),
    path('history/', views.food_history, name='food_history'),
    path('api/daily-calories/', views.api_daily_calories, name='api_daily_calories'),
]
