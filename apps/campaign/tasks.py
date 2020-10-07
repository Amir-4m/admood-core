from celery import shared_task
from django.db.models import Q
from django.utils.timezone import now

import datetime

from apps.campaign.models import Campaign, CampaignReference
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
            cr, created = CampaignReference.objects.get_or_create(
                campaign=campaign,
                date=today,
                max_view=campaign.remaining_views,
                start_time=schedule.start_time,
                end_time=schedule.end_time
            )
            if cr.reference_id:
                return
            # create telegram service campaign
            reference_id = create_campaign(
                campaign,
                datetime.datetime.combine(now().date(), schedule.start_time).__str__(),
                datetime.datetime.combine(now().date(), schedule.end_time).__str__(),
            )

            contents = campaign.contents.all()
            for content in contents:
                content_ref_id = create_content(content, reference_id)
                file = get_file(content.data.get('file', None))
                telegram_file_hash = content.data.get('telegram_file_hash', None)
                if file:
                    create_file(file, content_ref_id, telegram_file_hash)
                cr.contents.append({'content': content.pk, 'ref_id': content_ref_id, 'views': 0})

            if enable_campaign(reference_id):
                cr.reference_id = reference_id
                cr.save()


@shared_task
def update_telegram_view():
    campaign_refs = CampaignReference.objects.filter(
        reference_id__isnull=False,
        date=now().date(),
        end_time__lte=now().time(),
    )
    for campaign_ref in campaign_refs:
        reports = campaign_report(campaign_ref.reference_id)
        for content in campaign_ref.contents:
            for report in reports:
                if content["ref_id"] == report["content"]:
                    content["views"] = report["views"]
        campaign_ref.save()

        camp = campaign_ref.campaign
        if camp.campaignreference_set.count() == 1:
            ref_contents = get_contents(campaign_ref.reference_id)
            for ref_content in ref_contents:
                content = camp.contents.get(ref_content["id"])
                files = ref_content.get("files")
                for file in files:
                    content.data["telegram_file_hash"] = file.get("telegram_file_hash", None)
                    content.save()
                    # currently one file can be saved
                    break

