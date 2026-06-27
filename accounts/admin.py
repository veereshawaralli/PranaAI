from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone_number', 'is_patient', 'is_doctor', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone_number', 'date_of_birth', 'blood_group', 'address', 'is_patient', 'is_doctor')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
