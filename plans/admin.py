from django.contrib import admin
from .models import Preferences, Exercise_Plan, Exercise, Plan, User_Plan

# Register your models here.
admin.site.register(Preferences)
admin.site.register(Exercise_Plan)
admin.site.register(Exercise)
admin.site.register(Plan)
admin.site.register(User_Plan)
