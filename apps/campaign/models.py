import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from admood_core import settings
from apps.campaign.api.validators import validate_campaign_utm, validate_content_utm
from apps.device.consts import ServiceProvider
from apps.device.models import Device
from apps.medium.consts import Medium
from apps.medium.models import Publisher, Category


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    STATUS_WAITING = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (
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
    locations = models.ManyToManyField(Province)
    description = models.TextField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_WAITING)
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

        new_campaign = self
        new_campaign.pk = None
        new_campaign.status = Campaign.STATUS_WAITING
        new_campaign.save()
        new_campaign.publishers.set(publishers)
        new_campaign.locations.set(locations)
        new_campaign.categories.set(categories)

        for content in contents:
            new_content = content
            new_content.pk = None
            new_content.campaign = new_campaign
            new_content.save()

        for target_device in target_devices:
            new_target_device = target_device
            new_target_device.pk = None
            new_target_device.campaign = new_campaign
            new_target_device.save()

        for schedule in schedules:
            new_schedule = schedule
            new_schedule.pk = None
            new_schedule.campaign = new_campaign
            new_schedule.save()

        return new_campaign

@receiver(post_save, sender=Campaign)
def create_campaign(sender, instance, created, **kwargs):
    contents = instance.contents.all()

    import requests
    if created:
        return
    if instance.status != Campaign.STATUS_APPROVED:
        return
    url = 'http://192.168.2.152:8000/api/v1/campaign/'
    headers = {'Authorization': 'Token b962325ce06c24c8d322cb5a97ea3f7dbfdbd8a7'}
    data = dict(
        title=instance.name,
        status="approved",
        view_duration=None,
        is_enable=True,
        owner=1,
        categories=[
            instance.categories.values_list('pk', flat=True)
        ],
        channels=[
            instance.publishers.values_list('pk', flat=True)
        ],
        time_slicing=1
    )

    r = requests.post(url=url, headers=headers, data=data)
    if r.status_code != 201:
        return

    response = r.json()
    campaign_id = response['id']

    url = 'http://192.168.2.152:8000/api/v1/content/'
    headers = {'Authorization': 'Token b962325ce06c24c8d322cb5a97ea3f7dbfdbd8a7'}
    c = CampaignContent()

    for content in contents:
        data = dict(
            display_text=content.title,
            content=content.data,
            link="",
            has_tracker=True,
            tracker_bucket_size=10,
            view_type="total",
            message_id=None,
            is_sticker=False,
            campaign=1,
            mother_channel=1,
            tariff_publisher=None,
            tariff_advertiser=None
        )


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
    COST_MODEL_CPA = 1
    COST_MODEL_CPC = 2
    COST_MODEL_CPM = 3

    COST_MODEL_CHOICES = (
        (COST_MODEL_CPA, "cpa"),
        (COST_MODEL_CPC, "cpc"),
        (COST_MODEL_CPM, "cpm"),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=250)
    landing_url = models.URLField(blank=True, null=True)
    data = JSONField()
    utm = JSONField(validators=[validate_content_utm], null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    utm_term = models.CharField(max_length=100, blank=True, null=True)
    utm_content = models.CharField(max_length=50, null=True, blank=True)

    cost_model = models.PositiveSmallIntegerField(choices=COST_MODEL_CHOICES)
    cost_model_price = models.IntegerField()

    def __str__(self):
        return self.title


class CampaignSchedule(models.Model):
    SATURDAY = 0
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6

    DAYS_OF_WEEK = (
        (0, 'Saturday'),
        (1, 'Sunday'),
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='schedules')
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(default=datetime.time.min)
    end_time = models.TimeField(default=datetime.time.max)
