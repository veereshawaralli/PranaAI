"""
URL configuration for medibuddy_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve

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

# Static files: served by WhiteNoise in production, by Django in development.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media (user uploads) is served by Django in both dev and production so uploaded
# X-rays, meal photos, etc. render on the deployed site. NOTE: on hosts with an
# ephemeral filesystem (e.g. Render free tier) these uploads are wiped on every
# redeploy — move MEDIA to object storage (S3 / Cloudinary) for durable media.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
