from django.contrib import admin
from .models import SymptomCheck


@admin.register(SymptomCheck)
class SymptomCheckAdmin(admin.ModelAdmin):
    list_display = ('user', 'body_area', 'urgency_level', 'severity', 'created_at')
    list_filter = ('urgency_level', 'body_area', 'created_at')
    search_fields = ('user__username', 'body_area', 'additional_info')
