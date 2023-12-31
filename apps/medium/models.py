from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Max, Min
from django.db.models.functions import Coalesce

from .consts import Medium
from ..core.consts import CostModel


class Category(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    ref_id = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=50, db_index=True)
    display_text = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['medium', 'ref_id'], name="unique_medium_reference")
        ]

    def __str__(self):
        return f'{self.display_text}'


class CostModelPrice(models.Model):
    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    updated_time = models.DateTimeField(_("updated time"), auto_now=True)

    medium = models.PositiveSmallIntegerField(_("medium"), choices=Medium.MEDIUM_CHOICES)
    cost_model = models.PositiveSmallIntegerField(_("cost model"), choices=CostModel.COST_MODEL_CHOICES)
    grade = models.CharField(_("grade"), max_length=32)
    publisher_price = models.PositiveIntegerField(_("publisher price"))
    advertiser_price = models.PositiveIntegerField(_("advertiser price"))

    class Meta:
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        unique_together = ('medium', 'cost_model', 'grade',)

    def clean(self):
        if self.publisher_price >= self.advertiser_price:
            raise ValidationError(_('publisher price must be lower than advertiser price!'))

    def __str__(self):
        return f'G:{self.grade} - CM:{self.get_cost_model_display()}' \
               f' - PP:{self.publisher_price} - AP:{self.advertiser_price}'

    @staticmethod
    def max_price(publishers, cost_model):
        return CostModelPrice.objects.filter(publisher__in=publishers, cost_model=cost_model).aggregate(
            max_price=Coalesce(Max('advertiser_price'), 0)
        )['max_price']

    @staticmethod
    def min_price(publishers, cost_model):
        return CostModelPrice.objects.filter(publisher__in=publishers, cost_model=cost_model).aggregate(
            min_price=Coalesce(Min('advertiser_price'), 0)
        )['min_price']


class ApprovedPublisherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Publisher.STATUS_APPROVED, is_enable=True)


class Publisher(models.Model):
    STATUS_WAITING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2
    # STATUS_BLOCKED = 3

    STATUS_CHOICES = (
        (STATUS_WAITING, 'waiting'),
        (STATUS_APPROVED, 'approved'),
        (STATUS_REJECTED, 'rejected'),
        # (STATUS_BLOCKED, 'blocked'),
    )

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    cost_models = models.ManyToManyField(CostModelPrice, blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='publishers')

    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)
    extra_data = JSONField(null=True, blank=True)
    is_enable = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_WAITING)
    ref_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    objects = models.Manager()
    approved_objects = ApprovedPublisherManager()

    class Meta:
        unique_together = ['medium', 'ref_id']

    def __str__(self):
        return f'{self.name} - {self.get_medium_display()}'

    @staticmethod
    def get_by_categories(categories):
        return Publisher.objects.filter(categories__in=categories).distinct()
