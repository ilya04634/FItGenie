from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authUser.models import CustomUser

# Create your models here.
class Profile(models.Model):
    age = models.IntegerField(
        validators=[
            MinValueValidator(1),  # Минимальный возраст
            MaxValueValidator(120)  # Максимальный возраст
        ]
    )
    height = models.FloatField(
        validators=[
            MinValueValidator(30.0),  # Минимальная высота (в см)
            MaxValueValidator(250.0)  # Максимальная высота (в см)
        ]
    )
    weight = models.FloatField(
        validators=[
            MinValueValidator(2.0),  # Минимальный вес (в кг)
            MaxValueValidator(300.0)  # Максимальный вес (в кг)
        ]
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE) #нужно пересмотреть

    def __str__(self):
        return f"{self.user.nickname} - {self.age} лет"

