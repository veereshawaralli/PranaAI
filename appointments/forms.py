from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason_for_visit']
        widgets = {
            'reason_for_visit': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe your symptoms or reason for visit...'}),
        }
