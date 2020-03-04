from django.db import models
from admood_core import settings
from apps.core.constants import MediumType


class Publisher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medium_type = models.CharField(max_length=20, choices=MediumType.MEDIUM_TYPE_CHOICES)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=10)
    updated_time = models.DateTimeField(auto_now=True)
