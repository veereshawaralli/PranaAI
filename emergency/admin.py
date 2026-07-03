from django.contrib import admin
from .models import EmergencyContact, SOSAlert


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'relationship', 'phone_number', 'email', 'is_primary')
    list_filter = ('relationship', 'is_primary')
    search_fields = ('name', 'user__username', 'email')


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'contacts_notified', 'latitude', 'longitude', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
