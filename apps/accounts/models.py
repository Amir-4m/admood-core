from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ACTIVE = "Active"
    VERIFIED = "Verified"
    SUSPEND = "Suspend"
    WAITING = "Waiting"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (VERIFIED, "Verified"),
        (SUSPEND, "Suspend"),
        (WAITING, "Waiting"),
    )

    username = models.CharField(max_length=36, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.phone_number


class Profile(models.Model):
    REAL = "real"
    LEGAL = "legal"

    TYPE_CHOICES = (
        (REAL, "real"),
        (LEGAL, "legal"),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=REAL)
    image = models.ImageField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    national_id = models.CharField(max_length=10)
    street_address = models.CharField(max_length=10)
    post_code = models.CharField(max_length=10)
    id_location = models.CharField(max_length=10)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user


class Legal(models.Model):
    company_name = models.CharField(max_length=50)
    eco_code = models.CharField(max_length=10)
    register_code = models.CharField(max_length=10)


class Real(models.Model):
    pass
