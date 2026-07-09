from django.contrib import admin
from .models import MealPlan


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'dietary_preference', 'calorie_target', 'created_at')
    list_filter = ('goal', 'dietary_preference', 'created_at')
    search_fields = ('user__username',)
