from django.contrib import admin
from .models import FoodScan


@admin.register(FoodScan)
class FoodScanAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'calories', 'meal_type', 'user', 'scanned_at')
    list_filter = ('meal_type', 'scanned_at')
    search_fields = ('food_name', 'user__username')
