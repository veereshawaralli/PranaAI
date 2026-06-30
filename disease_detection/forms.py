from django import forms
from .models import DiseaseScan

class ScanUploadForm(forms.ModelForm):
    class Meta:
        model = DiseaseScan
        fields = ['image', 'scan_type']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'scan_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chest X-Ray, Brain MRI (Optional)'})
        }
