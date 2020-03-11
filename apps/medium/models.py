from django.db import models

from admood_core import settings
from .consts import Medium


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"


class MediumCategoryDisplayText(models.Model):
    medium = models.CharField(max_length=30, choices=Medium.MEDIUM_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    display_text = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['medium', 'category'], name="unique_medium_category")
        ]


class Publisher(models.Model):
    ACTIVE = "Active"
    SUSPEND = "Suspend"
    PAUSED = "Paused"
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
