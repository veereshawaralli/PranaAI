from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('add-reminder/', views.add_reminder, name='add_reminder'),
    path('edit-reminder/<int:pk>/', views.edit_reminder, name='edit_reminder'),
    path('delete-reminder/<int:pk>/', views.delete_reminder, name='delete_reminder'),
]
