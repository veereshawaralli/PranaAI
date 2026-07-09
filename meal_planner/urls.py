from django.urls import path
from . import views

app_name = 'meal_planner'

urlpatterns = [
    path('', views.generate_plan, name='generate_plan'),
    path('plan/<int:plan_id>/', views.view_plan, name='view_plan'),
    path('history/', views.plan_history, name='plan_history'),
]
