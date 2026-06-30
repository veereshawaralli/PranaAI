from django.db import models
from django.conf import settings

class DiseaseScan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='disease_scans')
    image = models.ImageField(upload_to='disease_scans/')
    scan_type = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., X-Ray, MRI")
    result_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.id} for {self.user.username}"
