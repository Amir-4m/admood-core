import datetime

from django.utils.timezone import now

from apps.campaign.models import CampaignReference, TelegramCampaign
from apps.core.utils.get_file import get_file
from services.telegram import create_campaign, create_content, create_file, enable_campaign, test_campaign


def next_weekday(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def create_telegram_campaign(campaign):
    if campaign.remaining_views <= 0:
        return
    schedules = campaign.schedules.order_by('week_day', 'start_time')
    if len(schedules) > 0:
        schedule = None
        for item in schedules:
            if not schedule:
                schedule = item
            if next_weekday(campaign.start_date, item.week_day) < next_weekday(campaign.start_date, schedule.week_day):
                schedule = item
        date = next_weekday(campaign.start_date, schedule.week_day)
        start_time = schedule.start_time
        end_time = schedule.ent_time
    else:
        date = campaign.start_date
        start_time = now().time().hour
        end_time = now().time()

    campaign_ref, created = CampaignReference.objects.get_or_create(
        campaign=campaign,
        date=date,
        max_view=campaign.remaining_views,
        start_time=start_time,
        end_time=end_time,
    )

    if campaign_ref.ref_id:
        return
    # create telegram service campaign
    ref_id = create_campaign(
        campaign,
        datetime.datetime.combine(date, start_time).__str__(),
        datetime.datetime.combine(date, end_time).__str__(),
        "approved",
    )

    screenshot = TelegramCampaign.objects.get(campaign=campaign).screenshot
    create_file(screenshot, ref_id)

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


def create_telegram_test_campaign(campaign):
    ref_id = create_campaign(
        campaign,
        now().__str__(),
        (now() + datetime.timedelta(hours=1)).__str__(),
        "test",
    )
    contents = campaign.contents.all()
    for content in contents:
        content_ref_id = create_content(content, ref_id)
        file = get_file(content.data.get('file', None))
        telegram_file_hash = content.data.get('telegram_file_hash', None)
        if file:
            create_file(file, content_ref_id, telegram_file_hash)

    return test_campaign(ref_id)
