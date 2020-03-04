from django.contrib.postgres.fields import JSONField
from django.db import models
from admood_core import settings
from apps.core.constants import MediumType, ServiceProvider, MediumInterface


class MediumCategory(models.Model):
    medium_type = models.CharField(max_length=30, choices=MediumType.MEDIUM_TYPE_CHOICES)
    medium_interface = models.CharField(max_length=30, choices=MediumInterface.MEDIUM_INTERFACE_CHOICES)


class Publisher(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medium_type = models.CharField(max_length=20, choices=MediumType.MEDIUM_TYPE_CHOICES)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=10)
    updated_time = models.DateTimeField(auto_now=True)


class Campaign(models.Model):
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    medium_type = models.CharField(max_length=20, choices=MediumType.MEDIUM_TYPE_CHOICES)
    service_provider = models.CharField(max_length=10, choices=ServiceProvider.SERVICE_PROVIDER_CHOICES)
    os = models.ForeignKey(OS, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
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
    campaign_status = models.CharField(max_length=20)
    is_enabled = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)


class CampaignContent(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    description = models.TextField()
    data = JSONField()
    landing_url = models.URLField()
    utm_term = models.CharField(max_length=100)
    image = models.ImageField()
