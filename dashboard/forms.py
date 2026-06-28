from django import forms
from .models import MedicineReminder

class MedicineReminderForm(forms.ModelForm):
    class Meta:
        model = MedicineReminder
        fields = ['medicine_name', 'dosage', 'frequency', 'time', 'is_active']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'})
        }
