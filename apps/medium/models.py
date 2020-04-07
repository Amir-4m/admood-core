from django.db import models

from admood_core import settings
from .consts import Medium


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MediumCategoryDisplayText(models.Model):
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    display_text = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['medium', 'category'], name="unique_medium_category")
        ]


class Publisher(models.Model):
    STATUS_ACTIVE = 1
    STATUS_SUSPEND = 2
    STATUS_PAUSED = 3
    STATUS_VERIFIED = 4

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPEND, "Suspend"),
        (STATUS_PAUSED, "PAUSED"),
        (STATUS_VERIFIED, "Verified"),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    categories = models.ManyToManyField(Category)

    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    description = models.TextField(null=True, blank=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
