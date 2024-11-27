# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# from django.db import models
# from django.utils import timezone
#
# class CustomUserManager(BaseUserManager):
#     def create_user(self, nickname, email, password=None, **extra_fields):
#         """
#         Создаёт и сохраняет пользователя с никнеймом и email.
#         """
#         if not email:
#             raise ValueError('Users must have an email address')
#         email = self.normalize_email(email)
#         user = self.model(nickname=nickname, email=email, **extra_fields)  # Передаем дополнительные поля через **extra_fields
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, nickname, email, password=None, **extra_fields):
#         """
#         Создаёт и сохраняет суперпользователя с никнеймом, email и паролем.
#         """
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#
#         return self.create_user(nickname, email, password, **extra_fields)
#
#
# class CustomUser(AbstractBaseUser):
#     email = models.EmailField(unique=True)
#     nickname = models.CharField(max_length=30, unique=True)
#     first_name = models.CharField(max_length=30, blank=True)
#     last_name = models.CharField(max_length=30, blank=True)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     date_joined = models.DateTimeField(default=timezone.now)
#
#     objects = CustomUserManager()
#
#     USERNAME_FIELD = 'nickname'  # Это будет полем для аутентификации
#     REQUIRED_FIELDS = ['email']  # Обязательно для superuser
#
#     def __str__(self):
#         return self.nickname


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, nickname, email, password=None, **extra_fields):
        """
        Создаёт и сохраняет пользователя с никнеймом и email.
        """
        if not email:
            raise ValueError("Users must have an email address")
        if not nickname:
            raise ValueError("Users must have a nickname")

        email = self.normalize_email(email)
        user = self.model(nickname=nickname, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, email, password=None, **extra_fields):
        """
        Создаёт и сохраняет суперпользователя.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(nickname, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Определяет доступ к админке
    is_superuser = models.BooleanField(default=False)  # Определяет суперпользователя
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'nickname'  # Поле для аутентификации
    REQUIRED_FIELDS = ['email']  # Поля, обязательные при создании суперпользователя

    def __str__(self):
        return self.nickname
