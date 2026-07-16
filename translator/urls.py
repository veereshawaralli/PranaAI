from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    path('', views.translator_home, name='home'),
    path('text/', views.text_translate, name='text_translate'),
    path('document/', views.document_translate, name='document_translate'),
    path('voice/', views.voice_translate, name='voice_translate'),
    path('voice/api/', views.voice_translate_api, name='voice_translate_api'),
    path('history/', views.translation_history, name='history'),
    path('history/delete/<int:pk>/', views.delete_translation, name='delete_translation'),
]
