from django.urls import path
from . import views

app_name = 'symptom_checker'

urlpatterns = [
    path('', views.checker_page, name='checker'),
    path('analyze/', views.analyze_symptoms, name='analyze'),
    path('history/', views.check_history, name='history'),
]
