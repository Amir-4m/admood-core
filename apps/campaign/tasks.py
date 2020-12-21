from datetime import datetime, timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import Q, Count
from django.utils.timezone import now

from apps.campaign.telegram import telegram
from admood_core.settings import ADBOT_MAX_CONCURRENT_CAMPAIGN
from apps.campaign.models import Campaign, CampaignReference, CampaignContent
from apps.core.utils.get_file import get_file
from apps.medium.consts import Medium
from apps.payments.models import Transaction
from services.instagram import create_insta_campaign, create_insta_content, create_insta_media, enable_Insta_campaign
from services.telegram import (
    campaign_report, get_contents, campaign_telegram_file_hash
)


@shared_task
def create_telegram_campaign_task():
    # filter approved and enable telegram campaigns
    campaigns = Campaign.objects.filter(
        is_enable=True,
        status=Campaign.STATUS_APPROVED,
        medium=Medium.TELEGRAM,
        start_date__lte=now().date(),
    )

    # disable expired and over budget campaigns
    for campaign in campaigns.all():
        if campaign.total_cost >= campaign.total_budget or (
                campaign.end_date is not None and campaign.end_date > now().date()):
            with transaction.atomic():
                # create a deduct transaction
                if campaign.total_cost > campaign.total_budget:
                    Transaction.objects.create(
                        user=campaign.owner,
                        value=campaign.total_cost - campaign.total_budget,
                        campaign=campaign,
                        transaction_type=Transaction.TYPE_DEDUCT,
                    )
                campaign.is_enable = False
                campaign.save()
                continue

        # if campaign doesn't have remaining views for today or at all
        if campaign.remaining_views <= 0:
            continue

    # create scheduled campaigns
    for campaign in campaigns.all():
        schedules = campaign.schedules.filter(
            week_day=now().date().weekday(),
            start_time__lte=now().time(),
            end_time__gt=now().time(),
        )
        for schedule in schedules.all():
            telegram.create_telegram_campaign(campaign, now().date(), schedule.start_time, schedule.end_time)

    # create non scheduled campaigns if possible
    concurrent_campaign_count = CampaignReference.objects.filter(
        ref_id__isnull=False,
        date=now().date(),
        updated_time__isnull=True
    ).count()
    if concurrent_campaign_count < ADBOT_MAX_CONCURRENT_CAMPAIGN:
        campaigns = campaigns.filter(
            schedules__isnull=True
        ).annotate(
            num_ref=Count('campaignreference')
        ).order_by('num_ref')
        for campaign in campaigns.all()[:ADBOT_MAX_CONCURRENT_CAMPAIGN - concurrent_campaign_count]:
            start_time = now().time()
            end_time = (now() + timedelta(hours=3)).time()
            telegram.create_telegram_campaign(campaign, now().date(), start_time, end_time)


# update content view in Campaign Reference model and add telegram file hashes
@shared_task
def update_telegram_info_task():
    # filter appropriate campaigns to save gotten views
    campaign_refs = CampaignReference.objects.filter(
        ref_id__isnull=False,
        date=now().date(),
        end_time__lte=now().time(),
        report_time__isnull=True,
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
        Q(is_enable=True),
        Q(status=Campaign.STATUS_APPROVED),
        Q(medium=Medium.INSTAGRAM_POST) | Q(medium=Medium.INSTAGRAM_STORY),
        Q(start_date__lte=today),
        Q(end_date__gte=today) | Q(end_date__isnull=True),
    )
    # first try to create scheduled campaigns
    scheduled_campaigns = campaigns.filter(schedules__week_day=today.weekday())
    for campaign in scheduled_campaigns:
        if campaign.remaining_views <= 0:
            continue
        schedules = campaign.schedules.filter(week_day=today.weekday())

        for schedule in schedules:
            campaign_ref, created = CampaignReference.objects.get_or_create(
                campaign=campaign,
                date=today,
                max_view=campaign.remaining_views,
                start_time=schedule.start_time,
                end_time=schedule.end_time
            )
            if campaign_ref.ref_id:
                continue
            # create instagram service campaign
            ref_id = create_insta_campaign(
                campaign,
                datetime.combine(now().date(), schedule.start_time).__str__(),
                datetime.combine(now().date(), schedule.end_time).__str__(),
                "approved",
            )

            content = campaign.contents.first()
            content_ref_id = create_insta_content(content, ref_id)
            file = get_file(content.data.get('file', None))

            if file:
                create_insta_media(file, content_ref_id)
            campaign_ref.contents.append({'content': content.pk, 'ref_id': content_ref_id, 'views': 0})

            if enable_Insta_campaign(ref_id):
                campaign_ref.ref_id = ref_id
                campaign_ref.save()
