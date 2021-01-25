from celery.schedules import crontab
from celery.task import periodic_task
from celery import shared_task
import logging

from django.db.models import Q
from django.utils import timezone
from django.db import transaction

from apps.campaign.models import Campaign, CampaignReference, CampaignContent
from apps.medium.consts import Medium
from apps.payments.models import Transaction

from .services import CampaignService, TelegramCampaignServices

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


@shared_task
def create_telegram_campaign_task():
    # filter approved and enable telegram campaigns
    campaigns = Campaign.live.filter(medium=Medium.TELEGRAM)
    CampaignService.create_campaign_by_medium(campaigns, 'telegram')


@shared_task
def create_instagram_campaign_task():
    campaigns = Campaign.live.filter(
        Q(medium=Medium.INSTAGRAM_POST) |
        Q(medium=Medium.INSTAGRAM_STORY)
    )
    CampaignService.create_campaign_by_medium(campaigns, 'instagram')


# update content view in Campaign Reference model and add telegram file hashes
@shared_task
def update_telegram_info_task():
    # filter appropriate campaigns to save gotten views
    campaign_refs = CampaignReference.live.all()

    for campaign_ref in campaign_refs:

        # store telegram file hash of screenshot in TelegramCampaign model
        campaign_ref.campaign.telegramcampaign.telegram_file_hash = TelegramCampaignServices().campaign_telegram_file_hash(campaign_ref.ref_id)

        # get each content views and store in content json field
        reports = TelegramCampaignServices().campaign_report(campaign_ref.ref_id)
        for content in campaign_ref.contents:
            for report in reports:
                if content["ref_id"] == report["content"]:
                    content["views"] = report["views"]
                    content["detail"] = report["detail"]
        campaign_ref.report_time = timezone.now()
        campaign_ref.save()

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
