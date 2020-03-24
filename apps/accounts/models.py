import random

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(extra_fields.get('email', ''))
        phone_number = self.normalize_email(extra_fields.get('phone_number', ''))
        username = self.model.normalize_username(username)
        try:
            assert username or email or phone_number, (
                _('at least one of username or email or phone_number must be set')
            )
        except AssertionError as e:
            raise ValueError(str(e))

        if username is None:
            if email:
                username = email.split('@', 1)[0]
            if phone_number:
                username = random.choice('abcdefghijklmnopqrstuvwxyz') + str(phone_number)[-7:]
            while User.objects.filter(username=username).exists():
                username += str(random.randint(10, 99))

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    username_validator = ASCIIUsernameValidator()

    ACTIVE = "Active"
    VERIFIED = "Verified"
    SUSPEND = "Suspend"
    WAITING = "Waiting"

    STATUS_CHOICES = (
        (ACTIVE, _("Activated")),
        (VERIFIED, _("Verified")),
        (SUSPEND, _("Suspended")),
        (WAITING, _("Waiting")),
    )

    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    updated_time = models.DateTimeField(_('updated time'), auto_now=True)

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    phone_number = models.BigIntegerField(
        _('phone number'),
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(r'^989[0-3,9]\d{8}$', _('Enter a valid phone number.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with this phone number already exists."),
        }
    )
    email = models.EmailField(_('email'), unique=True, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    status = models.CharField(_('user status'), max_length=10, choices=STATUS_CHOICES, db_index=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username


class Profile(models.Model):
    REAL = "rl"
    LEGAL = "lg"

    TYPE_CHOICES = (
        (REAL, _("real")),
        (LEGAL, _("legal")),
    )

    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    updated_time = models.DateTimeField(_('updated time'), auto_now=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=REAL)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(blank=True)
    bio = models.TextField(blank=True)
    national_id = models.CharField(max_length=10)
    street_address = models.CharField(max_length=10)
    post_code = models.CharField(max_length=10)
    id_location = models.CharField(max_length=10)
    company_name = models.CharField(max_length=50)
    eco_code = models.CharField(max_length=10)
    register_code = models.CharField(max_length=10)

    def __str__(self):
        return self.user
