from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Extending the default user with additional fields if necessary
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # We can add a boolean to quickly check if a user is a doctor or patient later if needed
    is_patient = models.BooleanField(default=True)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        return self.username
