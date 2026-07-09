from django import forms
from .models import FoodScan


class FoodScanForm(forms.ModelForm):
    class Meta:
        model = FoodScan
        fields = ['image', 'meal_type']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'meal_type': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'image': 'Meal Photo',
            'meal_type': 'Meal Type',
        }
