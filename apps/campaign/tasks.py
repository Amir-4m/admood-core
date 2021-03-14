import logging

from django.utils import timezone
from django.db import transaction
from django.conf import settings

from celery.schedules import crontab
from celery.task import periodic_task
from celery import shared_task

from apps.campaign.models import Campaign, CampaignReference, CampaignContent
from apps.medium.consts import Medium
from apps.payments.models import Transaction
from services.utils import stop_duplicate_task

from .services import CampaignService, TelegramCampaignServices
from .utils import update_campaign_reference_adtel

logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute="*"))
def disable_finished_campaigns():
    campaigns = Campaign.objects.select_for_update(skip_locked=True).filter(
        is_enable=True,
        status=Campaign.STATUS_APPROVED,
        start_date__lte=timezone.now().date(),
    )

    # disable expired and over budget campaigns
    with transaction.atomic():
        for campaign in campaigns:
            if campaign.is_finished():
                # create a deduct transaction
                Transaction.objects.create(
                    user=campaign.owner,
                    value=campaign.total_cost,
                    campaign=campaign,
                    transaction_type=Transaction.TYPE_DEDUCT,
                )
                campaign.is_enable = False
                campaign.save()


@periodic_task(run_every=crontab(minute="*/1"))
def create_telegram_campaign_task():
    create_telegram_campaign()


@stop_duplicate_task
def create_telegram_campaign():
    # filter approved and enable telegram campaigns
    campaigns = Campaign.objects.live().filter(medium=Medium.TELEGRAM, error_count__lt=5)
    CampaignService.create_campaign_by_medium(campaigns, 'telegram')


# update content view in Campaign Reference model and add telegram file hashes
@periodic_task(run_every=crontab(**settings.UPDATE_TELEGRAM_INFO_TASK_CRONTAB))
def update_telegram_info_task():
    # filter appropriate campaigns to save gotten views
    campaign_refs = CampaignReference.objects.monitor_report()

    for campaign_ref in campaign_refs:
        update_campaign_reference_adtel(campaign_ref)

        camp = campaign_ref.campaign
        # getting file hashes for the first campaign reference is enough
        if camp.campaignreference_set.count() == 1:
            for content in campaign_ref.contents:
                content_id = content["content"]
                for item in TelegramCampaignServices().get_contents(campaign_ref.ref_id):
                    if item["id"] == content["ref_id"]:
                        c = CampaignContent.objects.get(pk=content_id)
                        for file in item["files"]:
                            c.data["telegram_file_hash"] = file["telegram_file_hash"]
                            c.save()
                            # currently one file can be saved
                            break


@shared_task
def update_telegram_reports_from_admin(*campaign_references_id):
    for campaign_refs in CampaignReference.objects.filter(id__in=campaign_references_id):
        update_campaign_reference_adtel(campaign_refs)


# TODO create_instagram_campaign_task is disable for now
# @periodic_task(run_every=crontab())
# def create_instagram_campaign_task():
#     campaigns = Campaign.objects.live().filter(
#         Q(medium=Medium.INSTAGRAM_POST) |
#         Q(medium=Medium.INSTAGRAM_STORY),
#         error_count__lt=5
#     )
#     CampaignService.create_campaign_by_medium(campaigns, 'instagram')
