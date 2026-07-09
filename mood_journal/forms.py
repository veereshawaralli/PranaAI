from django import forms
from .models import MoodEntry
from django.utils import timezone


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood_score', 'journal_text', 'activities', 'sleep_hours', 'entry_date']
        widgets = {
            'mood_score': forms.HiddenInput(),
            'journal_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'How are you feeling today? Write about your thoughts, experiences, and emotions...',
            }),
            'activities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., exercise, work, reading, meditation, social',
            }),
            'sleep_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7.5',
                'step': '0.5',
                'min': '0',
                'max': '24',
            }),
            'entry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'mood_score': 'How are you feeling?',
            'journal_text': 'Journal Entry',
            'activities': 'Activities Today',
            'sleep_hours': 'Sleep Last Night (hours)',
            'entry_date': 'Date',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['entry_date'] = timezone.now().date().isoformat()
            self.initial['mood_score'] = 3
