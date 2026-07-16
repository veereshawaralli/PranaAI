from django.db import models
from django.conf import settings


class TranslationHistory(models.Model):
    """Stores every translation performed by a user."""

    TRANSLATION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('document', 'Document'),
        ('voice', 'Voice'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='translations',
    )
    translation_type = models.CharField(
        max_length=10,
        choices=TRANSLATION_TYPE_CHOICES,
        default='text',
    )
    source_language = models.CharField(max_length=50, default='Auto-Detect')
    target_language = models.CharField(max_length=50)
    original_text = models.TextField(blank=True, default='')
    translated_text = models.TextField(blank=True, default='')
    plain_explanation = models.TextField(
        blank=True,
        default='',
        help_text='Plain-language explanation of medical jargon.',
    )
    document_image = models.ImageField(
        upload_to='translator/documents/',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Translation histories'

    def __str__(self):
        return f"{self.user.username} — {self.translation_type} → {self.target_language} ({self.created_at:%Y-%m-%d %H:%M})"
