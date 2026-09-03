from django.contrib import admin

from .models import MealDay, MealOption, MealPlan

admin.site.register([MealPlan, MealDay, MealOption])
