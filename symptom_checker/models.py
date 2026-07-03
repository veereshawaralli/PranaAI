from django.db import models
from django.conf import settings
import json


class SymptomCheck(models.Model):
    """Stores each symptom check session and AI analysis result."""
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='symptom_checks'
    )
    body_area = models.CharField(max_length=50, blank=True, default='')
    symptoms_json = models.TextField(
        help_text="JSON array of selected symptoms",
        default='[]'
    )
    additional_info = models.TextField(blank=True, default='')
    duration = models.CharField(max_length=50, blank=True, default='')
    severity = models.IntegerField(default=5, help_text="1-10 scale")
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, default='')

    # AI Response
    ai_response = models.TextField(blank=True, default='')
    urgency_level = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        blank=True,
        default=''
    )
    possible_conditions = models.TextField(
        blank=True, default='',
        help_text="JSON array of possible conditions"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Symptom Check by {self.user.username} — {self.created_at:%b %d, %Y}"

    @property
    def symptoms_list(self):
        try:
            return json.loads(self.symptoms_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def conditions_list(self):
        try:
            return json.loads(self.possible_conditions)
        except (json.JSONDecodeError, TypeError):
            return []
