from django import forms
from .models import MealPlan


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['goal', 'dietary_preference', 'allergies', 'calorie_target']
        widgets = {
            'goal': forms.Select(attrs={'class': 'form-select'}),
            'dietary_preference': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., peanuts, shellfish, gluten (leave blank if none)',
            }),
            'calorie_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2000 (optional)',
                'min': 1000,
                'max': 5000,
            }),
        }
        labels = {
            'goal': 'Health Goal',
            'dietary_preference': 'Dietary Preference',
            'allergies': 'Food Allergies / Restrictions',
            'calorie_target': 'Daily Calorie Target (optional)',
        }
