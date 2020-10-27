import random
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, send_mail
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .tasks import send_verification_email, send_reset_password, send_verification_sms
from .validators import national_id_validator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username=None, password=None, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(extra_fields.get('email', None))
        phone_number = extra_fields.get('phone_number', None)
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

        user = self.model(username=username, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(username, password, **extra_fields)


class ActiveUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_verified=True, is_active=True)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = ASCIIUsernameValidator()

    STATUS_WAITING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2

    STATUS_CHOICES = (
        (STATUS_WAITING, _("waiting")),
        (STATUS_APPROVED, _("approved")),
        (STATUS_REJECTED, _("rejected")),
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
    is_verified = models.BooleanField(
        _('verified'),
        default=False
    )
    status = models.PositiveSmallIntegerField(_('user status'), choices=STATUS_CHOICES, default=STATUS_WAITING,
                                              db_index=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"

    class Meta:
        # db_table = 'auth_users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # @property
    # def is_loggedin_user(self):
    #     """
    #     Returns True if user has actually logged in with valid credentials.
    #     """
    #     return self.phone_number is not None or self.email is not None

    def save(self, *args, **kwargs):
        if self.email is not None and self.email.strip() == '':
            self.email = None
        super().save(*args, **kwargs)

    def verify(self):
        self.is_verified = True

    def send_verification_email(self):
        verification = self.verifications.create()
        send_verification_email.delay(self.email, verification.code)

    def send_verification_sms(self):
        verification = self.verifications.create()
        send_verification_sms.delay(self.phone_number, verification.code)

    def email_reset_password(self):
        verification = self.verifications.create()
        send_reset_password.delay(self.email, verification.uuid.hex)

    @staticmethod
    def get_by_email(email):
        try:
            return User.objects.get(email=email)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None


class UserProfile(models.Model):
    REAL = "rl"
    LEGAL = "lg"

    TYPE_CHOICES = (
        (REAL, _("real")),
        (LEGAL, _("legal")),
    )

    STATUS_WAITING = 0
    STATUS_REJECTED = 1
    STATUS_APPROVED = 2

    STATUS_CHOICES = (
        (STATUS_WAITING, _("waiting")),
        (STATUS_REJECTED, _("rejected")),
        (STATUS_APPROVED, _("approved")),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    updated_time = models.DateTimeField(_('updated time'), auto_now=True)

    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=REAL)
    status = models.PositiveSmallIntegerField(_('user status'), choices=STATUS_CHOICES, default=STATUS_WAITING,
                                              db_index=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    image = models.ImageField(null=True, blank=True)
    bio = models.TextField(blank=True)
    national_id = models.CharField(max_length=10, blank=True, validators=[national_id_validator])
    address = models.TextField(max_length=10, blank=True)
    post_code = models.CharField(max_length=10, blank=True)
    company_name = models.CharField(max_length=50, blank=True)
    eco_code = models.CharField(max_length=10, blank=True)
    register_code = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'accounts_profile'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return f'{self.first_name} {self.last_name}'.strip()


class Verification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    verified_time = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get(cls, uuid):
        return cls.objects.get(
            uuid=uuid,
            verified_time__isnull=True,
            created_time__gt=timezone.now() - timezone.timedelta(minutes=settings.USER_VERIFICATION_LIFETIME),
        )

    def is_valid(self):
        if self.verified_time:
            return False
        if self.created_time < timezone.now() - timezone.timedelta(minutes=settings.USER_VERIFICATION_LIFETIME):
            return False
        return True

    def verify(self):
        self.verified_time = timezone.now()
