from django.contrib import admin
from .models import MoodEntry


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood_score', 'ai_sentiment', 'entry_date', 'sleep_hours')
    list_filter = ('mood_score', 'ai_sentiment', 'entry_date')
    search_fields = ('user__username', 'journal_text')
