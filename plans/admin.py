from django.contrib import admin
from .models import Preferences, Weekly_Schedule, Exercises, Plan

# Register your models here.
admin.site.register(Preferences)
admin.site.register(Weekly_Schedule)
admin.site.register(Exercises)
admin.site.register(Plan)

