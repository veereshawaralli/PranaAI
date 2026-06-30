from django.urls import path
from . import views

app_name = 'disease_detection'

urlpatterns = [
    path('upload/', views.upload_scan, name='upload'),
    path('analyze/<int:scan_id>/', views.analyze_scan, name='analyze'),
    path('history/', views.scan_history, name='history'),
]
