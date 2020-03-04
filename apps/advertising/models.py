from django.contrib.postgres.fields import JSONField
from django.db import models
from admood_core import settings
from apps.core.constants import Medium, ServiceProvider


class Category(models.Model):
    name = models.CharField(max_length=50)


class MediumCategoryDisplayText(models.Model):
    medium = models.CharField(max_length=30, choices=Medium.MEDIUM_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    display_text = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['medium', 'category'], name="unique_medium_category")
        ]


class Platform(models.Model):
    name = models.CharField(max_length=50)


class OS(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class OSVersion(models.Model):
    os = models.ForeignKey(OS, on_delete=models.CASCADE)
    version = models.CharField(max_length=10)


class Publisher(models.Model):
    ACTIVE = "Active"
    SUSPEND = "Suspend"
    PAUSED = "PAUSED"
    VERIFIED = "Verified"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (SUSPEND, "Suspend"),
        (PAUSED, "PAUSED"),
        (VERIFIED, "Verified"),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medium = models.CharField(max_length=20, choices=Medium.MEDIUM_CHOICES)
    categories = models.ManyToManyField(Category)

    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    description = models.TextField(null=True, blank=True)
    updated_time = models.DateTimeField(auto_now=True)


class Campaign(models.Model):
    ACTIVE = "Active"
    SUSPEND = "Suspend"
    PAUSED = "PAUSED"
    VERIFIED = "Verified"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (SUSPEND, "Suspend"),
        (PAUSED, "PAUSED"),
        (VERIFIED, "Verified"),
    )

    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    medium = models.CharField(max_length=20, choices=Medium.MEDIUM_CHOICES)

    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    utm_source = models.CharField(max_length=50, null=True, blank=True)
    utm_medium = models.CharField(max_length=50, null=True, blank=True)
    utm_campaign = models.CharField(max_length=50, null=True, blank=True)
    utm_content = models.CharField(max_length=50, null=True, blank=True)

    cpm = models.CharField(max_length=50, null=True, blank=True)
    cpc = models.CharField(max_length=50, null=True, blank=True)
    cpa = models.CharField(max_length=50, null=True, blank=True)

    daily_cost = models.IntegerField()
    total_cost = models.IntegerField()
    finish_balance = models.IntegerField(null=True, blank=True)

    is_enabled = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)


class CampaignTargetDevice(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, null=True, blank=True)
    os = models.ForeignKey(OS, on_delete=models.CASCADE, null=True, blank=True)
    os_version = models.ForeignKey(OSVersion, on_delete=models.CASCADE, null=True, blank=True)
    service_provider = models.CharField(max_length=10, choices=ServiceProvider.SERVICE_PROVIDER_CHOICES,
                                        null=True, blank=True)


class CampaignContent(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    description = models.TextField()
    data = JSONField()
    landing_url = models.URLField()
    utm_term = models.CharField(max_length=100)
    image = models.ImageField()
