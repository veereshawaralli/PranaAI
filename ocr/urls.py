from django.urls import path
from . import views

app_name = 'ocr'

urlpatterns = [
    path('upload/', views.upload_prescription, name='upload'),
    path('confirm/', views.confirm_prescription, name='confirm'),
]
