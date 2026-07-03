from django.contrib import admin
from .models import HealthMetric


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'metric_type', 'value', 'secondary_value', 'recorded_at', 'created_at')
    list_filter = ('metric_type', 'recorded_at')
    search_fields = ('user__username', 'notes')
