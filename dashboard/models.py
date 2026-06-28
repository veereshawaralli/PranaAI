from django.db import models
from django.conf import settings

class MedicineReminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, help_text="e.g., 1 Pill, 10ml")
    frequency = models.CharField(max_length=50, help_text="e.g., Daily, Twice a day")
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine_name} for {self.user.username} at {self.time}"
