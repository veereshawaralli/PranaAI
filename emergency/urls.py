from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.sos_page, name='sos_page'),
    path('trigger/', views.trigger_sos, name='trigger_sos'),
    path('contacts/add/', views.add_contact, name='add_contact'),
    path('contacts/<int:pk>/edit/', views.edit_contact, name='edit_contact'),
    path('contacts/<int:pk>/delete/', views.delete_contact, name='delete_contact'),
    path('history/', views.sos_history, name='sos_history'),
]
