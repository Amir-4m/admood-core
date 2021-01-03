from celery import shared_task
from django.db.models import Q
from django.utils.timezone import now

from apps.campaign.models import Campaign, CampaignReference, CampaignContent
from apps.medium.consts import Medium
from services.telegram import campaign_report, get_contents, campaign_telegram_file_hash

from .services import CampaignService


@shared_task
def create_telegram_campaign_task():
    # filter approved and enable telegram campaigns
    campaigns = Campaign.objects.filter(
        Q(end_date__gte=now().date()) | Q(end_date__isnull=True),
        is_enable=True,
        status=Campaign.STATUS_APPROVED,
        medium=Medium.TELEGRAM,
        start_date__lte=now().date(),

    )
    CampaignService.create_campaign_by_medium(campaigns, 'telegram')


# update content view in Campaign Reference model and add telegram file hashes
@shared_task
def update_telegram_info_task():
    # filter appropriate campaigns to save gotten views
    campaign_refs = CampaignReference.objects.filter(
        ref_id__isnull=False,
        schedule_range__startswith__date=now().date(),
        schedule_range__endswith__time__lte=now().time(),
        updated_time__isnull=True,
    )
    for campaign_ref in campaign_refs:

        # store telegram file hash of screenshot in TelegramCampaign model
        campaign_ref.campaign.telegramcampaign.telegram_file_hash = campaign_telegram_file_hash(campaign_ref.ref_id)

        # get each content views and store in content json field
        reports = campaign_report(campaign_ref.ref_id)
        for content in campaign_ref.contents:
            for report in reports:
                if content["ref_id"] == report["content"]:
                    content["views"] = report["views"]
                    content["detail"] = report["detail"]
        campaign_ref.report_time = now()
        campaign_ref.save()

        camp = campaign_ref.campaign
        # getting file hashes for the first campaign reference is enough
        if camp.campaignreference_set.count() == 1:
            for content in campaign_ref.contents:
                content_id = content["content"]
                for item in get_contents(campaign_ref.ref_id):
                    if item["id"] == content["ref_id"]:
                        c = CampaignContent.objects.get(pk=content_id)
                        for file in item["files"]:
                            c.data["telegram_file_hash"] = file["telegram_file_hash"]
                            c.save()
                            # currently one file can be saved
                            break


@shared_task
def create_instagram_campaign():
    today = now().date()
    campaigns = Campaign.objects.filter(
        Q(medium=Medium.INSTAGRAM_POST) | Q(medium=Medium.INSTAGRAM_STORY),
        Q(end_date__gte=today) | Q(end_date__isnull=True),
        start_date__lte=today,
        is_enable=True,
        status=Campaign.STATUS_APPROVED,

    )
    CampaignService.create_campaign_by_medium(campaigns, 'instagram')
