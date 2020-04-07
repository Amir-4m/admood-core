from datetime import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from admood_core import settings
from apps.device.models import Platform, OS, OSVersion
from apps.device.consts import ServiceProvider
from apps.medium.consts import Medium
from apps.medium.models import Publisher


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    STATUS_WAITING = 1
    STATUS_VERIFIED = 2
    STATUS_SUSPEND = 3

    STATUS_CHOICES = (
        (STATUS_WAITING, "waiting"),
        (STATUS_VERIFIED, "verified"),
        (STATUS_SUSPEND, "suspend"),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)

    name = models.CharField(max_length=50)
    locations = models.ManyToManyField(Province)
    description = models.TextField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_WAITING)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    utm_source = models.CharField(max_length=50, null=True, blank=True)
    utm_medium = models.CharField(max_length=50, null=True, blank=True)
    utm_campaign = models.CharField(max_length=50, null=True, blank=True)
    utm_content = models.CharField(max_length=50, null=True, blank=True)

    daily_cost = models.IntegerField()
    total_cost = models.IntegerField()
    finish_balance = models.IntegerField(null=True, blank=True)

    is_enabled = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TargetDevice(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, null=True, blank=True)
    os = models.ForeignKey(OS, on_delete=models.CASCADE, null=True, blank=True)
    os_version = models.ForeignKey(OSVersion, on_delete=models.CASCADE, null=True, blank=True)
    service_provider = models.PositiveSmallIntegerField(choices=ServiceProvider.SERVICE_PROVIDER_CHOICES,
                                                        null=True, blank=True)

    def __str__(self):
        value = self.campaign
        if self.platform:
            value = f'{value}, {self.platform}'
        if self.os:
            value = f'{value}, {self.os}'
        if self.os_version:
            value = f'{value}, {self.os_version}'
        if self.service_provider:
            value = f'{value}, {self.service_provider}'
        return value

    def clean(self):
        if self.os_version:
            self.platform = self.os = None
        if self.os:
            self.platform = None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        return super().save()


class Content(models.Model):
    COST_MODEL_CPA = 1
    COST_MODEL_CPC = 2
    COST_MODEL_CPM = 3

    COST_MODEL_CHOICES = (
        (COST_MODEL_CPA, "cpa"),
        (COST_MODEL_CPC, "cpc"),
        (COST_MODEL_CPM, "cpm"),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    data = JSONField()
    description = models.TextField(blank=True, null=True)
    landing_url = models.URLField(blank=True, null=True)
    utm_term = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    cost_model = models.PositiveSmallIntegerField(choices=COST_MODEL_CHOICES)
    cost_model_price = models.IntegerField()

    def __str__(self):
        return self.title


class Schedule(models.Model):
    SATURDAY = 0
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6

    DAYS_OF_WEEK = (
        (0, 'Saturday'),
        (1, 'Sunday'),
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
