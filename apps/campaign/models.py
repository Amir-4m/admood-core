import datetime

from django.contrib.postgres.fields import JSONField, DateTimeRangeField
from django.db import models
from django.db.models import Max, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from admood_core import settings
from apps.core.consts import CostModel
from apps.core.models import File
from apps.device.consts import ServiceProvider
from apps.device.models import Device
from apps.medium.consts import Medium
from apps.medium.models import Publisher, Category


def json_default():
    return {'': ''}


# --- Custom Managers ---
class CampaignManager(models.Manager):

    def live(self):
        return self.get_queryset().filter(
            Q(end_date__gte=timezone.now().date()) | Q(end_date__isnull=True),
            is_enable=True,
            status=Campaign.STATUS_APPROVED,
            start_date__lte=timezone.now().date(),
        )


class CampaignReferenceManager(models.Manager):

    def live(self):
        return self.get_queryset().filter(
            ref_id__isnull=False,
            schedule_range__startswith__date=timezone.now().date(),
            schedule_range__endswith__time__lte=timezone.now().time(),
            report_time__isnull=True
        )


# --- Models ---
class Province(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    STATUS_DRAFT = 0
    STATUS_WAITING = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3
    # STATUS_BLOCKED = 4

    STATUS_CHOICES = (
        (STATUS_DRAFT, _("draft")),
        (STATUS_WAITING, _("waiting")),
        (STATUS_APPROVED, _("approved")),
        (STATUS_REJECTED, _("rejected")),
        # (STATUS_BLOCKED, _("blocked")),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medium = models.PositiveSmallIntegerField(choices=Medium.MEDIUM_CHOICES)
    publishers = models.ManyToManyField(Publisher, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    final_publishers = models.ManyToManyField(
        Publisher,
        through='FinalPublisher',
        blank=True,
        related_name='final_campaigns'
    )

    name = models.CharField(max_length=50)
    locations = models.ManyToManyField(Province, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT)
    start_date = models.DateField(default=datetime.date.today, blank=True)
    end_date = models.DateField(null=True, blank=True)

    extra_data = JSONField(default=json_default)

    utm_campaign = models.CharField(max_length=50, null=True, blank=True)
    utm_medium = models.CharField(max_length=50, null=True, blank=True)
    utm_content = models.CharField(max_length=50, null=True, blank=True)

    daily_budget = models.PositiveIntegerField()
    total_budget = models.PositiveIntegerField()

    is_enable = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)

    error_count = models.PositiveSmallIntegerField(default=0, editable=False)

    objects = CampaignManager()

    class Meta:
        ordering = ('-created_time',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._b_status = self.status

    def __str__(self):
        return self.name

    def is_finished(self):
        return (self.end_date and self.end_date < timezone.now().date()) or (self.total_cost >= self.total_budget)

    def update_final_publishers(self):
        # TODO Implement This
        # publishers_by_categories_ids = Publisher.get_by_categories(
        #     categories=instance.categories.all()
        # ).values_list('id', flat=True)
        # print(publishers_by_categories_ids)
        # current_publisher_ids = instance.publisher_price.all().values_list('publisher_id')
        # inserting_publisher = set(current_publisher_ids) - set(publishers_by_categories_ids)
        #
        # for publisher in Publisher.objects.filter(id__in=inserting_publisher):
        #     try:
        #         price = publisher.cost_models.filter(
        #                 cost_model=CostModel.CPV
        #             ).order_by('-publisher_price').first().publisher_price
        #     except:
        #         price = 0
        #     instance.publisher_price.create(
        #         publisher=publisher,
        #         publisher_price=price
        #     )
        #
        # current_publisher_ids = instance.publisher_price.all().values_list('publisher_id')
        # deleting_publisher_ids = set(publishers_by_categories_ids) - set(current_publisher_ids)
        # instance.publisher_price.filter(publisher_id__in=deleting_publisher_ids).delete()
        self.finalpublisher_set.all().delete()

        if self.categories.exists():
            publishers = Publisher.get_by_categories(
                categories=self.categories.all()
            )
        else:
            publishers = self.publishers.all()

        for publisher in publishers:
            try:
                price = publisher.cost_models.filter(
                        cost_model=CostModel.CPV
                    ).order_by('-publisher_price').first().publisher_price
            except:
                price = 0
            self.finalpublisher_set.create(publisher=publisher, tariff=price)

    @property
    def max_cost_model_price(self):
        return self.contents.aggregate(
            max_cost_model_price=Coalesce(Max('cost_model_price'), 0)
        )['max_cost_model_price']

    @property
    def remaining_views(self):
        budget = self.total_budget - self.total_cost
        if self.daily_budget:
            budget = min(self.daily_budget - self.today_cost, budget)
        if budget > 0 and self.max_cost_model_price > 0:
            return int(budget * 1000 / self.max_cost_model_price)
        return 0

    @property
    def total_cost(self):
        cost = 0
        for campaign_reference in self.campaignreference_set.filter(ref_id__isnull=False):
            if isinstance(campaign_reference.contents, list):
                for obj in campaign_reference.contents:
                    try:
                        content = self.contents.get(pk=obj['content'])
                        cost += obj['views'] * content.cost_model_price
                    except:
                        continue
        return cost

    @property
    def today_cost(self):
        cost = 0
        for campaign_reference in self.campaignreference_set.filter(
                created_time__date=timezone.now().date(),
                ref_id__isnull=False
        ):
            if isinstance(campaign_reference.contents, list):
                for obj in campaign_reference.contents:
                    try:
                        content = self.contents.get(pk=obj['content'])
                        cost += obj['views'] * content.cost_model_price
                    except:
                        continue
        return cost

    def approve_validate(self, status):
        if self.medium == Medium.TELEGRAM:
            if status == Campaign.STATUS_APPROVED and not hasattr(self, 'telegramcampaign'):
                return False, _('to approve the campaign upload the test screenshot.')

        # if status changed to approved, CampaignContent can not be empty
        if not self.contents.exists() and status == Campaign.STATUS_APPROVED:
            return False, _('to approve the campaign, content can not be empty!')

        return True, ''

    def create_publisher_list(self):
        pass


class FinalPublisher(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    tariff = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.publisher.name} - {self.tariff}"


class CampaignReference(models.Model):
    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    updated_time = models.DateTimeField(_("updated time"), auto_now=True)

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    ref_id = models.IntegerField(null=True, blank=True)
    extra_data = JSONField(default=json_default)
    contents = JSONField(default=list)
    max_view = models.IntegerField()
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    schedule_range = DateTimeRangeField(null=True, blank=True)
    report_time = models.DateTimeField(null=True, blank=True)

    objects = CampaignReferenceManager()


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
    data = JSONField(default=json_default)
    description = models.TextField(blank=True, null=True)
    utm_term = models.CharField(max_length=100, blank=True, null=True)

    cost_model = models.PositiveSmallIntegerField(choices=CostModel.COST_MODEL_CHOICES)
    cost_model_price = models.PositiveIntegerField()

    is_hidden = models.BooleanField(default=False)

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

    @property
    def campaign_medium(self):
        return self.campaign.medium

    @property
    def campaign_status(self):
        return self.campaign.status


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


class TelegramCampaign(models.Model):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
    screenshot = models.ForeignKey(File, on_delete=models.CASCADE)
    telegram_file_hash = models.CharField(max_length=512, blank=True)


class InstagramCampaign(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='instagram_campaigns')
    screenshot = models.ForeignKey(File, on_delete=models.CASCADE)
