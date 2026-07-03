from django import forms
from .models import HealthMetric
from django.utils import timezone


class HealthMetricForm(forms.ModelForm):
    class Meta:
        model = HealthMetric
        fields = ['metric_type', 'value', 'secondary_value', 'notes', 'recorded_at']
        widgets = {
            'metric_type': forms.Select(attrs={'class': 'form-select', 'id': 'metricType'}),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter value',
                'step': '0.1'
            }),
            'secondary_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Diastolic (for BP only)',
                'step': '0.1'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes (e.g., "after meal", "morning reading")'
            }),
            'recorded_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }
        labels = {
            'metric_type': 'Metric Type',
            'value': 'Value',
            'secondary_value': 'Secondary Value (BP Diastolic)',
            'notes': 'Notes',
            'recorded_at': 'Recorded At',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['recorded_at'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
