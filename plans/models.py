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


    goal = models.CharField(max_length=150)
    experience_level = models.CharField(max_length=1, choices=exp_level_Choice, default="B")
    workout_frequency = models.IntegerField( #сколько раз в неделю вы планируете тренироваться
        validators=[
            MinValueValidator(1),  # min value 1
            MaxValueValidator(7)  # max value 7
        ]
    )
    prefer_workout_ex = models.CharField(max_length=150)
    time_of_program = models.IntegerField(
        validators=[
            MinValueValidator(1),  # min value 1
            MaxValueValidator(12)  # max value 12
        ]
    )

    id_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.experience_level


class Plan(models.Model):
    name = models.CharField(max_length=25)
    created_by_ai = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class User_Plan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self


class Exercise(models.Model):
    name = models.CharField(max_length=30)
    sets = models.IntegerField(
        validators=[
            MinValueValidator(1),  # min value 1
            MaxValueValidator(10)  # max value 12
        ]
    )
    reps = models.IntegerField(null=True, blank=True)  # Опциональное поле для повторений
    duration = models.IntegerField(null=True, blank=True)  # Опциональное поле для времени выполнения

    def __str__(self):
        return self.name

class Exercise_Plan(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    def __str__(self):
        return self