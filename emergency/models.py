from django.db import models
from django.conf import settings


class EmergencyContact(models.Model):
    """Stores emergency contacts for a user."""
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('child', 'Child'),
        ('friend', 'Friend'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default='other')
    is_primary = models.BooleanField(default=False, help_text="Primary contact will be alerted first.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()}) - {self.user.username}"


class SOSAlert(models.Model):
    """Logs each SOS alert event."""
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sos_alerts'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    address = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    contacts_notified = models.IntegerField(default=0)
    message = models.TextField(blank=True, default='Emergency SOS Alert!')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SOS by {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"
