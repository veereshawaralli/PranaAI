from django.db import models
from django.conf import settings


class HealthMetric(models.Model):
    """Stores individual health metric readings for tracking over time."""
    METRIC_TYPE_CHOICES = [
        ('weight', 'Weight (kg)'),
        ('blood_pressure', 'Blood Pressure (mmHg)'),
        ('blood_sugar', 'Blood Sugar (mg/dL)'),
        ('heart_rate', 'Heart Rate (bpm)'),
        ('temperature', 'Temperature (°F)'),
        ('spo2', 'SpO2 (%)'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPE_CHOICES)
    value = models.DecimalField(max_digits=7, decimal_places=2, help_text="Primary value (systolic for BP)")
    secondary_value = models.DecimalField(
        max_digits=7, decimal_places=2,
        null=True, blank=True,
        help_text="Secondary value (diastolic for BP, leave blank for other metrics)"
    )
    notes = models.TextField(blank=True, default='')
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value} — {self.user.username}"

    @property
    def display_value(self):
        """Returns a human-readable value string."""
        if self.metric_type == 'blood_pressure' and self.secondary_value:
            return f"{self.value:.0f}/{self.secondary_value:.0f} mmHg"
        elif self.metric_type == 'weight':
            return f"{self.value:.1f} kg"
        elif self.metric_type == 'heart_rate':
            return f"{self.value:.0f} bpm"
        elif self.metric_type == 'blood_sugar':
            return f"{self.value:.0f} mg/dL"
        elif self.metric_type == 'temperature':
            return f"{self.value:.1f} °F"
        elif self.metric_type == 'spo2':
            return f"{self.value:.0f}%"
        return str(self.value)
