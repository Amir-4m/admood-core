from django.db import models
from .constants import MediumType, MediumInterface


class BaseModel(models.Model):
    pass

    class Meta:
        abstract = True


class MediumCategory(models.Model):
    medium_type = models.CharField(max_length=30, choices=MediumType.MEDIUM_TYPE_CHOICES)
    medium_interface = models.CharField(max_length=30, choices=MediumInterface.MEDIUM_INTERFACE_CHOICES)
