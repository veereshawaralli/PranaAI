from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('add-reminder/', views.add_reminder, name='add_reminder'),
]
