from datetime import datetime, timedelta

from django.utils.timezone import now

from apps.campaign.models import CampaignReference, TelegramCampaign
from apps.core.utils.get_file import get_file
from services.telegram import create_campaign, create_content, create_file, enable_campaign, test_campaign


def create_telegram_campaign(campaign, start_datetime, end_datetime):
    if campaign.error_count >= 5:
        return
    try:
        campaign_ref, created = CampaignReference.objects.get_or_create(
            campaign=campaign,
            schedule_range=(start_datetime, end_datetime),
            max_view=campaign.remaining_views,
        )
        if campaign_ref.ref_id:
            return
        # create telegram service
        ref_id = create_campaign(
            campaign,
            start_datetime,
            end_datetime,
            "approved",
        )

        telegram_campaign = TelegramCampaign.objects.get(campaign=campaign)
        telegram_file_hash = telegram_campaign.telegram_file_hash
        screenshot = TelegramCampaign.objects.get(campaign=campaign).screenshot.file
        create_file(file=screenshot, campaign_id=ref_id, telegram_file_hash=telegram_file_hash)

        contents = campaign.contents.all()
        for content in contents:
            content_ref_id = create_content(content, ref_id)
            file = get_file(content.data.get('file', None))
            telegram_file_hash = content.data.get('telegram_file_hash', None)
            if file:
                create_file(file, content_id=content_ref_id, telegram_file_hash=telegram_file_hash)
            campaign_ref.contents.append({'content': content.pk, 'ref_id': content_ref_id, 'views': 0})

        if enable_campaign(ref_id):
            campaign_ref.ref_id = ref_id
            campaign_ref.save()
            return campaign_ref
    except Exception as e:
        campaign.error_count += 1
        campaign.save()
        raise e


def create_telegram_test_campaign(campaign):
    ref_id = create_campaign(
        campaign,
        now().__str__(),
        (now() + timedelta(hours=1)).__str__(),
        "test",
    )
    contents = campaign.contents.all()
    for content in contents:
        content_ref_id = create_content(content, ref_id)
        file = get_file(content.data.get('file', None))
        telegram_file_hash = content.data.get('telegram_file_hash', None)
        if file:
            create_file(file, content_id=content_ref_id, telegram_file_hash=telegram_file_hash)

    return test_campaign(ref_id)
