import logging

from datetime import datetime, timedelta

import requests
from django.db import transaction
from django.db.models import Count, Q
from django.utils.timezone import now

from admood_core.settings import (
    ADBOT_MAX_CONCURRENT_CAMPAIGN, ADINSTA_API_TOKEN, ADINSTA_API_URL
)
from apps.core.consts import CostModel
from apps.core.utils.get_file import get_file
from apps.campaign.models import CampaignSchedule, CampaignReference, TelegramCampaign
from apps.payments.models import Transaction
from services.telegram import create_campaign, create_content, create_file, enable_campaign, test_campaign
from services.utils import file_type

logger = logging.getLogger(__name__)


class InstagramCampaignServices(object):
    JSON_HEADERS = {
        'Authorization': ADINSTA_API_TOKEN,
        'Content-type': 'application/json'
    }
    HEADERS = {
        'Authorization': ADINSTA_API_TOKEN,
    }

    CAMPAIGN_URL = f'{ADINSTA_API_URL}/api/v1/campaigns/'
    CONTENT_URL = f'{ADINSTA_API_URL}/api/v1/contents/'
    FILE_URL = f'{ADINSTA_API_URL}/api/v1/files/'
    MEDIA_URL = f'{ADINSTA_API_URL}/api/v1/medias/'
    PAGES_URL = f'{ADINSTA_API_URL}/api/v1/instagram/pages/'

    def api_call(self, method, url, data=None, params=None, files=None):
        try:
            if method.lower() == 'get':
                response = requests.get(url=url, headers=self.HEADERS, params=params)
            elif method.lower() == 'post':
                response = requests.post(url=url, headers=self.HEADERS, json=data, files=files)
            else:
                return None
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f'{method} api call {url} got error: {e}')
            return

    def create_insta_campaign(self, campaign, start_time, end_time, status):
        publishers = []
        for publisher in campaign.final_publishers.all():
            try:
                publisher_price = publisher.cost_models.filter(
                    Q(cost_model=CostModel.CPI) | Q(cost_model=CostModel.CPR)
                ).order_by('-publisher_price').first().publisher_price
            except:
                publisher_price = 0
            publishers.append((publisher.ref_id, publisher_price))
        data = dict(
            title=campaign.name,
            status=status,
            is_enable=False,
            publishers=publishers,
            campaign_type=campaign.get_medium_display().split('_')[1],
            start_datetime=start_time,
            end_datetime=end_time,
        )
        response = self.api_call('post', url=self.CAMPAIGN_URL, data=data)
        return response.json()['id']

    def create_insta_content(self, content, campaign_id):
        data = dict(
            campaign=campaign_id,
            title=content.title,
            caption=content.data.get('content'),
            description=content.description
        )
        response = self.api_call('post', url=self.CONTENT_URL, data=data)

        return response.json()['id']

    def create_insta_media(self, file, content_id):
        data = dict(
            file_type=file_type(file.name),
            content=content_id,
        )

        self.api_call('post', url=self.MEDIA_URL, data=data, files={'file': file})

    def enable_Insta_campaign(self, campaign_id):
        self.api_call('post', url=f'{self.CAMPAIGN_URL}{campaign_id}/', data={'is_enable': True})
        return True

    def get_insta_publishers(self):
        response = self.api_call('get', url=self.PAGES_URL)
        return response.json()

    def get_insta_campaign(self, campaign_id):
        response = self.api_call('get', url=f'{self.CAMPAIGN_URL}{campaign_id}/')
        return response.json()

    def get_contents(self, campaign_id):
        campaign = self.get_insta_campaign(campaign_id)
        contents = campaign.get('contents', None)
        return contents

    @staticmethod
    def create_instagram_campaign(campaign, start_datetime, end_datetime):
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
            # create instagram service
            ref_id = InstagramCampaignServices().create_insta_campaign(
                campaign,
                start_datetime,
                end_datetime,
                "approved",
            )

            content = campaign.contents.first()
            content_ref_id = InstagramCampaignServices().create_insta_content(content, ref_id)
            file = get_file(content.data.get('file', None))

            if file:
                InstagramCampaignServices().create_insta_media(file, content_ref_id)
            campaign_ref.contents.append({'content': content.pk, 'ref_id': content_ref_id, 'views': 0})

            if InstagramCampaignServices().enable_Insta_campaign(ref_id):
                campaign_ref.ref_id = ref_id
                campaign_ref.save()
                return campaign_ref
        except Exception as e:
            logger.error(f'creating instagram campaign with id {campaign.id} failed due to : {e}')
            campaign.error_count += 1
            campaign.save()
            raise e


class TelegramCampaignServices(object):
    @staticmethod
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
            logger.error(f'creating telegram campaign with id {campaign.id} failed due to : {e}')
            campaign.error_count += 1
            campaign.save()
            raise e

    @staticmethod
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


class CampaignService(object):
    @staticmethod
    def create_campaign_by_medium(campaigns, medium):
        try:
            create_campaign_func = {
                'instagram': InstagramCampaignServices.create_instagram_campaign,
                'telegram': TelegramCampaignServices.create_telegram_campaign
            }[medium]
        except KeyError:
            raise Exception('invalid medium. choices are: instagram, telegram')

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
        schedules = CampaignSchedule.objects.filter(
            campaign_id__in=campaigns.values_list('id', flat=True),
            week_day=now().date().weekday(),
            start_time__lte=now().time(),
            end_time__gt=now().time(),
        )

        for schedule in schedules.all():
            schedule_lower_range = datetime.now().replace(
                hour=schedule.start_time.hour,
                minute=schedule.start_time.minute
            )

            schedule_upper_range = datetime.now().replace(
                hour=schedule.end_time.hour,
                minute=schedule.end_time.minute
            )

            create_campaign_func(schedule.campaign, schedule_lower_range, schedule_upper_range)

        # create non scheduled campaigns if possible
        concurrent_campaign_count = CampaignReference.objects.filter(
            ref_id__isnull=False,
            schedule_range__startswith__date=now().date(),
            updated_time__isnull=True
        ).count()
        if concurrent_campaign_count < ADBOT_MAX_CONCURRENT_CAMPAIGN:
            campaigns = campaigns.filter(
                schedules__isnull=True
            ).annotate(
                num_ref=Count('campaignreference')
            ).order_by('num_ref')
            for campaign in campaigns.all()[:ADBOT_MAX_CONCURRENT_CAMPAIGN - concurrent_campaign_count]:
                start_datetime = datetime.now()
                end_datetime = start_datetime + timedelta(hours=3)
                create_campaign_func(campaign, start_datetime, end_datetime)
