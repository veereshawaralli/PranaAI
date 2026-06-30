from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('update-status/<int:appointment_id>/<str:status>/', views.update_status, name='update_status'),
]
