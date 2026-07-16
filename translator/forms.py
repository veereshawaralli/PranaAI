from django import forms


LANGUAGE_CHOICES = [
    ('Hindi', 'Hindi (हिन्दी)'),
    ('Kannada', 'Kannada (ಕನ್ನಡ)'),
    ('Tamil', 'Tamil (தமிழ்)'),
    ('Telugu', 'Telugu (తెలుగు)'),
    ('Malayalam', 'Malayalam (മലയാളം)'),
    ('Marathi', 'Marathi (मराठी)'),
    ('Bengali', 'Bengali (বাংলা)'),
    ('Gujarati', 'Gujarati (ગુજરાતી)'),
    ('Punjabi', 'Punjabi (ਪੰਜਾਬੀ)'),
    ('Urdu', 'Urdu (اردو)'),
    ('Spanish', 'Spanish (Español)'),
    ('French', 'French (Français)'),
    ('German', 'German (Deutsch)'),
    ('Arabic', 'Arabic (العربية)'),
    ('Mandarin Chinese', 'Mandarin Chinese (中文)'),
    ('Japanese', 'Japanese (日本語)'),
    ('Korean', 'Korean (한국어)'),
    ('Portuguese', 'Portuguese (Português)'),
    ('Russian', 'Russian (Русский)'),
    ('Thai', 'Thai (ไทย)'),
]


class TextTranslationForm(forms.Form):
    text_to_translate = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Paste or type your medical text here…\n\nExamples:\n• Doctor\'s instructions\n• Lab report findings\n• Prescription notes\n• Discharge summary',
            'id': 'id_text_to_translate',
        }),
        label='Medical Text',
    )
    target_language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_target_language',
        }),
        label='Translate To',
    )


class DocumentTranslationForm(forms.Form):
    document_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_document_image',
        }),
        label='Upload Medical Document / Lab Report Image',
    )
    target_language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_target_language_doc',
        }),
        label='Translate To',
    )
