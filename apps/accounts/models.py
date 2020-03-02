from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.core.models import BaseModel
from .managers import UserManager


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    phone_number = models.CharField(_('phone number'), max_length=11, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number


class Profile(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
