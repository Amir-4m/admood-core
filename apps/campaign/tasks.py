from celery import shared_task
from django.db.models import Q
from django.utils.timezone import now

import datetime

from apps.campaign.models import Campaign, CampaignReference
from apps.core.utils.get_file import get_file
from services.telegram import create_campaign, create_content, create_file, enable_campaign, campaign_report
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
                content_id = create_content(content, reference_id)
                file = get_file(content.data.get('file', None))
                telegram_file_hash = content.data.get('telegram_file_hash', None)
                if file:
                    create_file(file, content_id, telegram_file_hash)

            if enable_campaign(reference_id):
                cr.reference_id = reference_id
                cr.save()


@shared_task
def update_telegram_view():
    campaign_references = CampaignReference.objects.filter(
        reference_id__isnull=False,
        report__isnull=True,
        end_time__lte=now().time(),
    )
    for campaign_reference in campaign_references:
        report = campaign_report(campaign_reference.reference_id)
        if report:
            campaign_reference.report = report
            campaign_reference.save()

