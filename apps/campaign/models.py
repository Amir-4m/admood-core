from django.db import models

from admood_core import settings
from apps.core.constants import MediumType
from apps.publish.models import Publisher


class Campaign(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    medium_type = models.CharField(max_length=20, choices=MediumType.MEDIUM_TYPE_CHOICES)
    # objective =
    # ad =
    # schedule =
    # device =
    # location =
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
    daily_cost = models.DecimalField(max_digits=20, decimal_places=2)
    total_cost = models.DecimalField(max_digits=20, decimal_places=2)
    finish_balance = models.DecimalField(max_digits=20, decimal_places=2)
    campaign_status = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)
    is_enabled = models.BooleanField(default=True)
