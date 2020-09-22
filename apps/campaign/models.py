import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Max
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _

from admood_core import settings
from apps.core.consts import CostModel
from apps.campaign.api.validators import validate_campaign_utm, validate_content_utm
from apps.core.models import File
from apps.device.consts import ServiceProvider
from apps.device.models import Device
from apps.medium.consts import Medium
from apps.medium.models import Publisher, Category


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    STATUS_DRAFT = 0
    STATUS_WAITING = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (
        (STATUS_DRAFT, "draft"),
        (STATUS_WAITING, "waiting"),
        (STATUS_APPROVED, "approved"),
        (STATUS_REJECTED, "rejected"),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    reference_id = models.BigIntegerField(null=True, blank=True)
    publishers = models.ManyToManyField(Publisher, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    name = models.CharField(max_length=50)
    locations = models.ManyToManyField(Province, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT)
    start_date = models.DateField(default=datetime.date.today, blank=True)
    end_date = models.DateField(null=True, blank=True)

    utm_source = models.CharField(max_length=50, null=True, blank=True)
    utm_medium = models.CharField(max_length=50, null=True, blank=True)
    utm_campaign = models.CharField(max_length=50, null=True, blank=True)

    utm = JSONField(validators=[validate_campaign_utm], null=True, blank=True)

    daily_cost = models.PositiveIntegerField()
    total_cost = models.PositiveIntegerField()
    finish_balance = models.IntegerField(null=True, blank=True)

    is_enable = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clone(self):
        publishers = self.publishers.all()
        locations = self.locations.all()
        categories = self.categories.all()
        contents = self.contents.all()
        target_devices = self.target_devices.all()
        schedules = self.schedules.all()

        self.pk = None
        self.status = Campaign.STATUS_WAITING
        self.save()
        self.publishers.set(publishers)
        self.locations.set(locations)
        self.categories.set(categories)

        for content in contents:
            content = content
            content.pk = None
            content.campaign = self
            content.save()

        for target_device in target_devices:
            target_device = target_device
            target_device.pk = None
            target_device.campaign = self
            target_device.save()

        for schedule in schedules:
            schedule = schedule
            schedule.pk = None
            schedule.campaign = self
            schedule.save()

        return self

    @property
    def max_view(self):
        max_cpv = self.contents.aggregate(
            max_cost_model_price=Coalesce(Max('cost_model_price'), 0)
        )['max_cost_model_price']
        if max_cpv:
            return int(self.total_cost / max_cpv)
        else:
            return 0


class CampaignReference(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    reference_id = models.IntegerField(null=True, blank=True)
    report = JSONField(null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


class TargetDevice(models.Model):
    SERVICE_PROVIDER_MTN = 1
    SERVICE_PROVIDER_MCI = 2
    SERVICE_PROVIDER_RTL = 3

    SERVICE_PROVIDER_CHOICES = (
        (SERVICE_PROVIDER_MTN, "MTN"),
        (SERVICE_PROVIDER_MCI, "MCI"),
        (SERVICE_PROVIDER_RTL, "RTL"),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='target_devices')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    service_provider = models.PositiveSmallIntegerField(choices=ServiceProvider.SERVICE_PROVIDER_CHOICES,
                                                        null=True, blank=True)


class CampaignContent(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=250)
    landing_url = models.URLField(blank=True, null=True)
    data = JSONField()
    description = models.TextField(blank=True, null=True)
    utm_term = models.CharField(max_length=100, blank=True, null=True)
    utm_content = models.CharField(max_length=50, null=True, blank=True)

    cost_model = models.PositiveSmallIntegerField(choices=CostModel.COST_MODEL_CHOICES)
    cost_model_price = models.IntegerField()

    class Meta:
        verbose_name = 'Content'
        ordering = ['pk']

    def __str__(self):
        return self.title

    @property
    def file(self):
        try:
            return File.objects.get(pk=self.data.get('file', None)).file
        except File.DoesNotExist:
            return None


class CampaignSchedule(models.Model):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    WEEKDAYS = (
        (MONDAY, _('Monday')),
        (TUESDAY, _('Tuesday')),
        (WEDNESDAY, _('Wednesday')),
        (THURSDAY, _('Thursday')),
        (FRIDAY, _('Friday')),
        (SATURDAY, _('Saturday')),
        (SUNDAY, _('Sunday')),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='schedules')
    week_day = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time = models.TimeField(default=datetime.time.min)
    end_time = models.TimeField(default=datetime.time.max)

    class Meta:
        verbose_name = 'Schedule'


class CampaignPublisher(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    publisher_price = models.PositiveIntegerField()
    advertiser_price = models.PositiveIntegerField()
