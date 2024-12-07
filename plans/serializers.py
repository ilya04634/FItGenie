from rest_framework import serializers
from .models import Preferences, Plan, Exercises, Weekly_Schedule

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        # fields = ["goal", 'experience_level', 'workout_frequency', 'prefer_workout_ex', 'time_of_program']
        fields = '__all__'


    def create(self, validated_data):
        return Preferences.objects.create(**validated_data)


    def update(self, instance, validated_data):
        instance.experience_level = validated_data.pop("experience_level")
        instance.goal = validated_data.pop("goal")
        instance.workout_frequency = validated_data.pop("workout_frequency")
        instance.prefer_workout_ex = validated_data.pop("prefer_workout_ex")
        instance.time_of_program = validated_data.pop("time_of_program")


        instance.save()
        return instance


# class ExerciseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Exercises
#         fields = ['name', 'sets', 'reps', 'rest', 'notes']
#
#
# class WeeklyScheduleSerializer(serializers.ModelSerializer):
#     exercises = ExerciseSerializer(many=True)
#
#     class Meta:
#         model = Weekly_Schedule
#         fields = ['day', 'focus', 'exercises']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercises
        fields = ["id", "name", "sets", "reps", "rest", "notes"]

class WeeklyScheduleSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True, source="exercises_set")

    class Meta:
        model = Weekly_Schedule
        fields = ["id", "day", "focus", "exercises"]

class PlanDetailSerializer(serializers.ModelSerializer):
    weekly_schedule = WeeklyScheduleSerializer(many=True, read_only=True, source="weekly_schedule_set")

    class Meta:
        model = Plan
        fields = ["id", "name", "description", "program_duration", "weekly_schedule"]

class PlanSerializer(serializers.ModelSerializer):
    weekly_schedule = WeeklyScheduleSerializer(many=True)

    class Meta:
        model = Plan
        fields = ['name', 'description', 'program_duration', 'weekly_schedule']

    def create(self, validated_data):
        weekly_schedule_data = validated_data.pop('weekly_schedule')

        plan = Plan.objects.create(**validated_data)

        for schedule_data in weekly_schedule_data:
            exercises_data = schedule_data.pop('exercises')

            schedule = Weekly_Schedule.objects.create(plan_id=plan, **schedule_data)


            for exercise_data in exercises_data:
                Exercises.objects.create(weekly_schedule_id=schedule, **exercise_data)

        return plan


