from django.db import models

from .consts import Medium
from ..core.consts import CostModel


class Category(models.Model):
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=50, db_index=True)
    display_text = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['medium', 'reference_id'], name="unique_medium_reference")
        ]

    def __str__(self):
        return f'{self.get_medium_display()} - {self.display_text}'


class CostModelPrice(models.Model):
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    cost_model = models.CharField(max_length=3, choices=CostModel.COST_MODEL_CHOICES)
    grade = models.PositiveSmallIntegerField()
    publisher_price = models.PositiveIntegerField()
    advertiser_price = models.PositiveIntegerField()

    class Meta:
        unique_together = ('medium', 'cost_model', 'grade',)

    def __str__(self):
        return f'{self.grade}-{self.get_medium_display()}'


class Publisher(models.Model):
    cost_models = models.ManyToManyField(CostModelPrice, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)
    is_enable = models.BooleanField()
    reference_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
