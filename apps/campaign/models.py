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
    VERIFIED = "verified"
    SUSPEND = "suspend"
    PAUSED = "paused"

    STATUS_CHOICES = (
        (VERIFIED, "verified"),
        (SUSPEND, "suspend"),
        (PAUSED, "paused"),
    )

    CPA = "cpa"
    CPC = "cpc"
    CPM = "cpm"

    AD_MODEL_CHOICES = (
        (CPA, "cpa"),
        (CPC, "cpc"),
        (CPM, "cpm"),
    )

    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    medium = models.CharField(max_length=20, choices=Medium.MEDIUM_CHOICES)

    name = models.CharField(max_length=50)
    locations = models.ManyToManyField(Province)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    utm_source = models.CharField(max_length=50, null=True, blank=True)
    utm_medium = models.CharField(max_length=50, null=True, blank=True)
    utm_campaign = models.CharField(max_length=50, null=True, blank=True)
    utm_content = models.CharField(max_length=50, null=True, blank=True)

    cost_model = models.CharField(max_length=50, choices=AD_MODEL_CHOICES, null=True, blank=True)

    daily_cost = models.IntegerField()
    total_cost = models.IntegerField()
    finish_balance = models.IntegerField(null=True, blank=True)

    is_enabled = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CampaignTargetDevice(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, null=True, blank=True)
    os = models.ForeignKey(OS, on_delete=models.CASCADE, null=True, blank=True)
    os_version = models.ForeignKey(OSVersion, on_delete=models.CASCADE, null=True, blank=True)
    service_provider = models.CharField(max_length=10, choices=ServiceProvider.SERVICE_PROVIDER_CHOICES,
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


class CampaignContent(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    data = JSONField()
    description = models.TextField(blank=True, null=True)
    landing_url = models.URLField(blank=True, null=True)
    utm_term = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    cost_model_price = models.IntegerField()

    def __str__(self):
        return self.title
