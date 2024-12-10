from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authUser.models import CustomUser
# Create your models here.


class Preferences(models.Model):
    exp_level_Choice = [
        ("B", 'beginner'),
        ("M", 'middle'),
        ("P", 'professional'),
    ]
    gender_choice = [
        ("M", 'male'),
        ("F", 'female')
    ]

    gender = models.CharField(max_length=1, choices=gender_choice)
    age = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(120)
        ]
    )
    height = models.FloatField(
        validators=[
            MinValueValidator(30.0),
            MaxValueValidator(250.0)
        ]
    )
    weight = models.FloatField(
        validators=[
            MinValueValidator(2.0),
            MaxValueValidator(300.0)
        ]
    )
    goal = models.CharField(max_length=150)
    experience_level = models.CharField(max_length=1, choices=exp_level_Choice, default="B")
    workout_frequency = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7)
        ]
    )
    prefer_workout_ex = models.CharField(max_length=150)
    time_of_program = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12)
        ]
    )

    id_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='preferences')

    def __str__(self):
        return f"{self.id_user} | {self.goal} | {self.experience_level}"


class Plan(models.Model):
    id_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    id_preferences = models.ForeignKey(Preferences, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    description = models.TextField(null=True, blank=True)
    program_duration = models.IntegerField(null=True, blank=True)


    def __str__(self):
        return self.name


class Weekly_Schedule(models.Model):
    plan_id = models.ForeignKey(Plan, on_delete=models.CASCADE)
    day = models.CharField(max_length=15, null=True)
    focus = models.CharField(max_length=350, null=True)

    def __str__(self):
        return self.focus



class Exercises(models.Model):
    weekly_schedule_id = models.ForeignKey(Weekly_Schedule, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    sets = models.CharField(max_length=15, null=True, blank=True)
    reps = models.CharField(max_length=15, null=True, blank=True)
    rest = models.CharField(max_length=25, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name











#
# class User_Plan(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self
#
#
# class Exercise(models.Model):
#     name = models.CharField(max_length=30)
#     sets = models.IntegerField(
#         validators=[
#             MinValueValidator(1),  # min value 1
#             MaxValueValidator(10)  # max value 12
#         ]
#     )
#     reps = models.IntegerField(null=True, blank=True)  # Опциональное поле для повторений
#     duration = models.IntegerField(null=True, blank=True)  # Опциональное поле для времени выполнения
#
#     def __str__(self):
#         return self.name
#
# class Exercise_Plan(models.Model):
#     plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
#     exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self