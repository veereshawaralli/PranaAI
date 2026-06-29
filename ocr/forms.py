from django import forms

class PrescriptionUploadForm(forms.Form):
    image = forms.ImageField(
        label='Select Prescription Image',
        help_text='Upload a clear photo of your medical prescription.'
    )
