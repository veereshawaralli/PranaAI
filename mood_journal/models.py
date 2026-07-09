from django.db import models
from django.conf import settings


class MoodEntry(models.Model):
    """A single daily mood journal entry with AI sentiment analysis."""
    MOOD_CHOICES = [
        (1, 'Awful'),
        (2, 'Bad'),
        (3, 'Okay'),
        (4, 'Good'),
        (5, 'Great'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_entries'
    )
    mood_score = models.IntegerField(choices=MOOD_CHOICES, default=3)
    journal_text = models.TextField(blank=True, default='', help_text='Write about your day')
    activities = models.CharField(
        max_length=300, blank=True, default='',
        help_text='Comma-separated tags (e.g., exercise, work, social)'
    )
    sleep_hours = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True,
        help_text='Hours of sleep last night'
    )
    ai_sentiment = models.CharField(
        max_length=20, choices=SENTIMENT_CHOICES,
        blank=True, default=''
    )
    ai_analysis = models.TextField(blank=True, default='', help_text='AI mental health insights')
    entry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date']
        unique_together = ['user', 'entry_date']

    def __str__(self):
        return f"{self.get_mood_score_display()} — {self.entry_date} — {self.user.username}"

    @property
    def mood_emoji(self):
        emojis = {1: '😢', 2: '😟', 3: '😐', 4: '😊', 5: '🤩'}
        return emojis.get(self.mood_score, '😐')

    @property
    def mood_color(self):
        colors = {1: '#EF4444', 2: '#F97316', 3: '#EAB308', 4: '#10B981', 5: '#06B6D4'}
        return colors.get(self.mood_score, '#94A3B8')

    @property
    def activity_list(self):
        """Returns activities as a list of stripped tags."""
        if not self.activities:
            return []
        return [a.strip() for a in self.activities.split(',') if a.strip()]
