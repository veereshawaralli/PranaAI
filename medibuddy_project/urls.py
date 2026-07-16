"""
URL configuration for medibuddy_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('reports/', include('reports.urls')),
    path('ocr/', include('ocr.urls')),
    path('disease-detection/', include('disease_detection.urls')),
    path('locator/', include('locator.urls')),
    path('appointments/', include('appointments.urls')),
    path('emergency/', include('emergency.urls')),
    path('analytics/', include('analytics.urls')),
    path('symptom-checker/', include('symptom_checker.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('diet/', include('diet_tracker.urls')),
    path('meal-planner/', include('meal_planner.urls')),
    path('mood-journal/', include('mood_journal.urls')),
    path('translator/', include('translator.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
