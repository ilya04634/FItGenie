from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, nickname, email, password=None, **extra_fields):
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
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['email']

    @staticmethod
    def get_email_field_name():
        return 'email'
    def __str__(self):
        return f"{self.nickname} - {'Verified' if self.is_verified else 'Not Verified'}"


