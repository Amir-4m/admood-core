from celery import shared_task
from django.utils.timezone import now

from apps.campaign.models import Campaign, MediumCampaign
from apps.campaign.telegram import create_campaign
from apps.campaign.telegram.telegram import campaign_report
from apps.medium.consts import Medium


@shared_task
def create_telegram_campaign():
    today = now().date()
    campaigns = Campaign.objects.filter(
        is_enable=True,
        status=Campaign.STATUS_APPROVED,
        medium=Medium.TELEGRAM,
        start_date__lte=today,
        end_date__gte=today,
        # schedules__week_day=today.weekday()
    )

    scheduled_campaigns = campaigns.filter(schedules__week_day=today.weekday())

    for campaign in scheduled_campaigns:
        schedules = campaign.schedules.filter(week_day=today.weekday())

        for schedule in schedules:
            cm, created = MediumCampaign.objects.get_or_create(
                campaign=campaign,
                date=today,
                start_time=schedule.start_time,
                end_time=schedule.end_time
            )
            if cm.reference_id:
                # update report data
                data = campaign_report(cm.reference_id)
                if data:
                    cm.data = data
                    cm.save()
            else:
                # create telegram service campaign
                cm.reference_id = create_campaign(campaign, str(schedule.start_time), str(schedule.end_time))
                cm.save()

    # todo create non schedule campaigns
    if len(scheduled_campaigns) < 5:
        pass


@shared_task
def disable_telegram_campaign():
    # disable telegram campaign
    pass
