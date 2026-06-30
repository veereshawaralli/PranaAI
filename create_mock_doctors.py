import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medibuddy_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from appointments.models import DoctorProfile

User = get_user_model()

doctors_data = [
    {
        'username': 'dr_smith',
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'smith@example.com',
        'specialty': 'Cardiologist',
        'experience_years': 15,
        'consultation_fee': 150.00,
        'bio': 'Specializing in heart conditions and preventative care.'
    },
    {
        'username': 'dr_jones',
        'first_name': 'Sarah',
        'last_name': 'Jones',
        'email': 'jones@example.com',
        'specialty': 'Neurologist',
        'experience_years': 10,
        'consultation_fee': 200.00,
        'bio': 'Expert in disorders of the nervous system.'
    },
    {
        'username': 'dr_patel',
        'first_name': 'Vikram',
        'last_name': 'Patel',
        'email': 'patel@example.com',
        'specialty': 'General Physician',
        'experience_years': 8,
        'consultation_fee': 75.00,
        'bio': 'Comprehensive care for families and individuals of all ages.'
    }
]

for data in doctors_data:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'is_doctor': True,
            'is_patient': False
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"Created user {user.username}")
        
    profile, p_created = DoctorProfile.objects.get_or_create(
        user=user,
        defaults={
            'specialty': data['specialty'],
            'experience_years': data['experience_years'],
            'consultation_fee': data['consultation_fee'],
            'bio': data['bio']
        }
    )
    if p_created:
        print(f"Created profile for {user.username}")

print("Mock doctors generated successfully!")
