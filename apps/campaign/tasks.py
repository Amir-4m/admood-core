from celery import shared_task
from django.db.models import Q
from django.utils.timezone import now

import datetime

from apps.campaign.models import Campaign, CampaignReference, CampaignContent
from apps.core.utils.get_file import get_file
from services.telegram import create_campaign, create_content, create_file, enable_campaign, campaign_report, \
    get_contents
from apps.medium.consts import Medium


@shared_task
def create_telegram_campaign():
    today = now().date()
    campaigns = Campaign.objects.filter(
        Q(is_enable=True),
        Q(status=Campaign.STATUS_APPROVED),
        Q(medium=Medium.TELEGRAM),
        Q(start_date__lte=today),
        Q(end_date__gte=today) | Q(end_date__isnull=True),
    )

    # first try to create scheduled campaigns
    # for telegram bot
    scheduled_campaigns = campaigns.filter(schedules__week_day=today.weekday())
    for campaign in scheduled_campaigns:
        if campaign.remaining_views <= 0:
            return
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
                return
            # create telegram service campaign
            ref_id = create_campaign(
                campaign,
                datetime.datetime.combine(now().date(), schedule.start_time).__str__(),
                datetime.datetime.combine(now().date(), schedule.end_time).__str__(),
                "approved",
            )

            contents = campaign.contents.all()
            for content in contents:
                content_ref_id = create_content(content, ref_id)
                file = get_file(content.data.get('file', None))
                telegram_file_hash = content.data.get('telegram_file_hash', None)
                if file:
                    create_file(file, content_ref_id, telegram_file_hash)
                campaign_ref.contents.append({'content': content.pk, 'ref_id': content_ref_id, 'views': 0})

            if enable_campaign(ref_id):
                campaign_ref.ref_id = ref_id
                campaign_ref.save()


@shared_task
def update_telegram_view():
    campaign_refs = CampaignReference.objects.filter(
        ref_id__isnull=False,
        date=now().date(),
        end_time__lte=now().time(),
    )
    for campaign_ref in campaign_refs:
        reports = campaign_report(campaign_ref.ref_id)
        for content in campaign_ref.contents:
            for report in reports:
                if content["ref_id"] == report["content"]:
                    content["views"] = report["views"]
        campaign_ref.save()

        camp = campaign_ref.campaign
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
