from django.urls import path
from . import views

app_name = 'mood_journal'

urlpatterns = [
    path('', views.journal_dashboard, name='dashboard'),
    path('check-in/', views.check_in, name='check_in'),
    path('entry/<int:entry_id>/', views.entry_detail, name='entry_detail'),
    path('api/mood-data/', views.api_mood_data, name='api_mood_data'),
    path('api/weekly-insight/', views.weekly_insight, name='weekly_insight'),
]
