from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('add/', views.add_metric, name='add_metric'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/health-score/', views.health_score, name='health_score'),
]
