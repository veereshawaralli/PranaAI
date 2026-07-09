from django.db import models
from django.conf import settings


class FoodScan(models.Model):
    """Stores a single food scan — an uploaded meal photo analyzed by Gemini AI."""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_scans'
    )
    image = models.ImageField(upload_to='food_scans/')
    food_name = models.CharField(max_length=200, blank=True, default='')
    calories = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    protein = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    carbs = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    fat = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    fiber = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='lunch')
    ai_analysis = models.TextField(blank=True, default='', help_text='Full AI analysis response')
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.food_name or 'Food Scan'} — {self.calories or '?'} kcal — {self.user.username}"

    @property
    def macro_total(self):
        """Returns the total of protein + carbs + fat for percentage calculations."""
        p = float(self.protein or 0)
        c = float(self.carbs or 0)
        f = float(self.fat or 0)
        return p + c + f or 1  # avoid division by zero
