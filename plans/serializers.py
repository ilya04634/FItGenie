from rest_framework import serializers
from .models import Preferences, Plan, User_Plan, Exercise, Exercise_Plan

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Plan
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class ExercisePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise_Plan
        fields = '__all__'