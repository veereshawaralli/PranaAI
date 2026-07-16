from django.contrib import admin
from .models import TranslationHistory


@admin.register(TranslationHistory)
class TranslationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'translation_type', 'target_language', 'created_at')
    list_filter = ('translation_type', 'target_language', 'created_at')
    search_fields = ('user__username', 'original_text', 'translated_text')
    readonly_fields = ('created_at',)
