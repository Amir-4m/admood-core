import logging

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from django.conf import settings

from apps.core.utils.get_file import get_file
from apps.campaign.models import CampaignSchedule, CampaignReference, TelegramCampaign
from services.utils import file_type, custom_request

logger = logging.getLogger(__name__)


class InstagramCampaignServices(object):
    JSON_HEADERS = {
        'Authorization': settings.ADINSTA_API_TOKEN,
        'Content-type': 'application/json'
    }
    HEADERS = {
        'Authorization': settings.ADINSTA_API_TOKEN,
    }

    CAMPAIGN_URL = f'{settings.ADINSTA_API_URL}/api/v1/campaigns/'
    CONTENT_URL = f'{settings.ADINSTA_API_URL}/api/v1/contents/'
    FILE_URL = f'{settings.ADINSTA_API_URL}/api/v1/files/'
    MEDIA_URL = f'{settings.ADINSTA_API_URL}/api/v1/medias/'
    PAGES_URL = f'{settings.ADINSTA_API_URL}/api/v1/instagram/pages/'

    def create_insta_campaign(self, campaign, start_time, end_time, status):
        logger.debug(
            f"[creating instagram campaign]-[obj: {campaign}]-[start time: {start_time}]-[end time: {end_time}]"
            f"-[status: {status}]-[URL: {self.CAMPAIGN_URL}]"
        )
        publishers = []
        for final_publisher in campaign.finalpublisher_set.all():
            publishers.append((final_publisher.publisher.ref_id, final_publisher.tariff))
        data = dict(
            title=campaign.name,
            status=status,
            is_enable=False,
            publishers=publishers,
            campaign_type=campaign.get_medium_display().split('_')[1],
            start_datetime=start_time,
            end_datetime=end_time,
        )
        response = custom_request(self.CAMPAIGN_URL, json=data, headers=self.HEADERS)
        return response.json()['id']

    def create_insta_content(self, content, campaign_id):
        logger.debug(
            f"[creating instagram content]-[content id: {content.id}]-[campaign id: {campaign_id}]"
            f"-[URL: {self.CONTENT_URL}]"
        )
        data = dict(
            campaign=campaign_id,
            title=content.title,
            caption=content.data.get('content'),
            description=content.description
        )
        response = custom_request(self.CONTENT_URL, json=data, headers=self.HEADERS)
        return response.json()['id']

    def create_insta_media(self, file, content_id):
        logger.debug(
            f"[creating instagram media]-[file: {file.name}]-[content id: {content_id}]-[URL: {self.MEDIA_URL}]"
        )

        data = dict(
            file_type=file_type(file.name),
            content=content_id,
        )
        custom_request(self.MEDIA_URL, json=data, files={'file': file}, headers=self.HEADERS)

    def enable_Insta_campaign(self, campaign_id):
        url = f'{self.CAMPAIGN_URL}{campaign_id}/'
        logger.debug(f"[enabling instagram campaign]-[campaign id: {campaign_id}]-[URL: url]")

        custom_request(url, 'patch', json={'is_enable': True}, headers=self.HEADERS)
        return True

    def get_insta_publishers(self):
        logger.debug(f'[getting instagram publishers]')

        response = custom_request(self.PAGES_URL, 'get', headers=self.HEADERS)
        return response.json()

    def get_insta_campaign(self, campaign_id):
        url = f'{self.CAMPAIGN_URL}{campaign_id}/'
        logger.debug(f'[getting instagram campaign]-[campaign id: {campaign_id}]-[URL: {url}]')

        response = custom_request(url, 'get', headers=self.HEADERS)
        return response.json()

    def get_contents(self, campaign_id):
        logger.debug(f'[getting contents]-[campaign id: {campaign_id}]')

        campaign = self.get_insta_campaign(campaign_id)
        contents = campaign.get('contents', None)
        return contents

    @staticmethod
    def create_instagram_campaign(campaign, start_datetime, end_datetime):
        logger.debug(
            f"[creating instagram campaign]-[campaign id: {campaign.id}]-[start time: {start_datetime}]-[end time: {end_datetime}]"
        )
        if campaign.error_count >= 5:
            logger.error(f"[creating instagram campaign failed]-[campaign id: {campaign.id}]")
            return

        if CampaignReference.objects.filter(
                campaign=campaign,
                ref_id__isnull=False,
                schedule_range__startswith__lte=timezone.now(),
                schedule_range__endswith__gte=timezone.now(),
        ).exists():
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
            campaign.error_count += 1
            campaign.save()
            logger.error(f'[creating instagram campaign failed]-[campaign id: {campaign.id}]-'
                         f'[error count:{campaign.error_count}]-[exc: {e}]')
            raise e


class TelegramCampaignServices(object):
    HEADERS = {
        'Authorization': settings.ADBOT_API_TOKEN,
    }

    CAMPAIGN_URL = f'{settings.ADBOT_API_URL}/api/v1/campaigns/'
    CONTENT_URL = f'{settings.ADBOT_API_URL}/api/v1/contents/'
    FILE_URL = f'{settings.ADBOT_API_URL}/api/v1/files/'
    CHANNELS_URL = f'{settings.ADBOT_API_URL}/api/v1/channels/'

    def create_campaign(self, campaign, start_time, end_time, status):
        logger.debug(
            f"[creating telegram campaign]-[campaign id: {campaign.id}]-[start time: {start_time}]-"
            f"[end time: {end_time}]-[status: {status}]-[URL: {self.CAMPAIGN_URL}]"
        )
        publishers = []
        for final_publisher in campaign.finalpublisher_set.all():
            publishers.append((final_publisher.publisher.ref_id, final_publisher.tariff))

        data = dict(
            title=campaign.name,
            status=status,
            is_enable=False,
            publishers=publishers,
            max_view=campaign.remaining_views,
            agents=[settings.ADBOT_AGENTS],
            post_limit=campaign.extra_data.get('post_limit'),
            start_datetime=str(start_time),
            end_datetime=str(end_time),
        )
        response = custom_request(self.CAMPAIGN_URL, json=data, headers=self.HEADERS)
        return response.json()['id']

    def create_content(self, content, campaign_id):
        logger.debug(
            f"[creating telegram content]-[content id: {content.id}]-[campaign id: {campaign_id}]"
            f"-[URL: {self.CONTENT_URL}]"
        )

        if 'post_link' in content.data:
            data = dict(
                campaign=campaign_id,
                display_text=content.title,
                post_link=content.data.get('post_link'),
                view_type=content.data.get('view_type'),
                mother_channel=content.data.get('mother_channel', None),
            )
        else:
            utm_source = "admood"
            utm_campaign = content.campaign.utm_campaign
            utm_medium = content.campaign.utm_medium
            utm_content = content.campaign.utm_content

            if utm_campaign is None:
                utm_campaign = content.campaign.pk
            if utm_medium is None:
                utm_medium = content.campaign.get_medium_display()

            links = content.data.get('links', [])
            for i, link in enumerate(links, 1):
                link['utm_source'] = utm_source
                link["utm_campaign"] = utm_campaign
                link["utm_medium"] = utm_medium
                if utm_content is not None:
                    link['utm_content'] = utm_content
                if link.get('utm_term') is None:
                    link['utm_term'] = i

            inlines = content.data.get('inlines', [])
            for i, inline in enumerate(inlines, 1):
                if inline.get('has_tracker'):
                    inline['utm_source'] = utm_source
                    inline["utm_campaign"] = utm_campaign
                    inline["utm_medium"] = utm_medium
                    if utm_content is not None:
                        inline['utm_content'] = utm_content
                    if inline.get('utm_term') is None:
                        inline['utm_term'] = i
                else:
                    inline.pop('utm_term')

            data = dict(
                campaign=campaign_id,
                display_text=content.title,
                content=content.data.get('content'),
                links=links,
                inlines=inlines,
                is_sticker=content.data.get('is_sticker', False),
                mother_channel=content.data.get('mother_channel', None),
                view_type=content.data.get('view_type'),
            )

        response = custom_request(self.CONTENT_URL, json=data, headers=self.HEADERS)
        return response.json()['id']

    def create_file(self, file, campaign_id=None, content_id=None, telegram_file_hash=None):
        filetype = file_type(file.name)

        logger.debug(
            f"[creating telegram file]-[file: {file.name}]-[file type: {filetype}]-[content id: {content_id}]"
            f"-[telegram file hash: {telegram_file_hash}]-[URL: {self.FILE_URL}]"
        )
        data = dict(
            name=file.name,
            file_type=filetype,
            telegram_file_hash=telegram_file_hash
        )
        if campaign_id:
            data['campaign'] = campaign_id
        if content_id:
            data['campaign_content'] = content_id

        if telegram_file_hash:
            custom_request(self.FILE_URL, json=data, headers=self.HEADERS)
        else:
            custom_request(self.FILE_URL, data=data, files={'file': file}, headers=self.HEADERS)

    def enable_campaign(self, campaign_id):
        url = f'{self.CAMPAIGN_URL}{campaign_id}/'
        logger.debug(f'[enabling telegram campaign]-[campaign id: {campaign_id}]-[URL: {url}]')

        custom_request(url, 'patch', json={'is_enable': True}, headers=self.HEADERS)
        return True

    def campaign_report(self, campaign_id):
        url = f'{self.CAMPAIGN_URL}{campaign_id}/report/'
        logger.debug(f'[getting telegram report]-[campaign id: {campaign_id}]-[URL: {url}]')

        response = custom_request(url, 'get', headers=self.HEADERS)
        return response.json()

    def get_publishers(self):
        logger.debug(f'[getting telegram publishers]-[URL: {self.CHANNELS_URL}]')

        response = custom_request(self.CHANNELS_URL, 'get', headers=self.HEADERS)
        return response.json()

    def get_campaign(self, campaign_id):
        url = f'{self.CAMPAIGN_URL}{campaign_id}/'
        logger.debug(f'[getting telegram campaign]-[campaign id: {campaign_id}]-[URL: {url}]')

        response = custom_request(url, 'get', headers=self.HEADERS)
        return response.json()

    def get_contents(self, campaign_id):
        campaign = self.get_campaign(campaign_id)
        contents = campaign.get('contents', None)
        return contents

    def campaign_telegram_file_hash(self, campaign_id):
        campaign = self.get_campaign(campaign_id)
        file = campaign.get('file')
        if file:
            return file.get('telegram_file_hash')

    def test_campaign(self, campaign_id):
        url = f'{self.CAMPAIGN_URL}{campaign_id}/test/'
        logger.debug(f'[testing telegram campaign]-[campaign id: {campaign_id}]-[URL: {url}]')

        response = custom_request(url, 'get', timeout=120, headers=self.HEADERS)
        return response.json()["detail"]

    @staticmethod
    def create_telegram_campaign(campaign, start_datetime, end_datetime):
        start_datetime = start_datetime.replace(second=0, microsecond=0)
        end_datetime = end_datetime.replace(second=0, microsecond=0)

        if campaign.error_count >= 5:
            logger.error(f"[creating telegram campaign failed]-[campaign id: {campaign.id}]")
            return

        if CampaignReference.objects.filter(
                campaign=campaign,
                ref_id__isnull=False,
                schedule_range__startswith__lte=timezone.now(),
                schedule_range__endswith__gte=timezone.now(),
        ).exists():
            return

        try:
            campaign_ref = CampaignReference.objects.create(
                campaign=campaign,
                schedule_range=(start_datetime, end_datetime),
                max_view=campaign.remaining_views,
            )

            # create telegram service
            ref_id = TelegramCampaignServices().create_campaign(
                campaign,
                start_datetime,
                end_datetime,
                "approved",
            )

            telegram_campaign = TelegramCampaign.objects.get(campaign=campaign)
            telegram_file_hash = telegram_campaign.telegram_file_hash
            screenshot = TelegramCampaign.objects.get(campaign=campaign).screenshot.file
            TelegramCampaignServices().create_file(
                file=screenshot, campaign_id=ref_id,
                telegram_file_hash=telegram_file_hash
            )

            contents = campaign.contents.all()
            for content in contents:
                content_ref_id = TelegramCampaignServices().create_content(content, ref_id)
                file = get_file(content.data.get('file', None))
                telegram_file_hash = content.data.get('telegram_file_hash', None)
                if file:
                    TelegramCampaignServices().create_file(
                        file,
                        content_id=content_ref_id,
                        telegram_file_hash=telegram_file_hash
                    )
                campaign_ref.contents.append({'content': content.pk, 'ref_id': content_ref_id, 'views': 0})

            if TelegramCampaignServices().enable_campaign(ref_id):
                campaign_ref.ref_id = ref_id
                campaign_ref.save()
                return campaign_ref
        except Exception as e:
            logger.error(f'[creating telegram campaign failed]-[campaign id: {campaign.id}]-[exc: {e}]')
            campaign.error_count += 1
            campaign.save()
            raise e

    @staticmethod
    def create_telegram_test_campaign(campaign):
        ref_id = TelegramCampaignServices().create_campaign(
            campaign,
            timezone.now().__str__(),
            (timezone.now() + timedelta(hours=1)).__str__(),
            "test",
        )
        contents = campaign.contents.all()
        for content in contents:
            content_ref_id = TelegramCampaignServices().create_content(content, ref_id)
            file = get_file(content.data.get('file', None))
            telegram_file_hash = content.data.get('telegram_file_hash', None)
            if file:
                TelegramCampaignServices().create_file(
                    file, content_id=content_ref_id,
                    telegram_file_hash=telegram_file_hash
                )

        return TelegramCampaignServices().test_campaign(ref_id)


class CampaignService(object):
    @staticmethod
    def create_campaign_by_medium(campaigns, medium):
        logger.debug(f'[creating campaing by medium]-[medium: {medium}]')
        try:
            create_campaign_func = {
                'instagram': InstagramCampaignServices.create_instagram_campaign,
                'telegram': TelegramCampaignServices.create_telegram_campaign
            }[medium]
        except KeyError as e:
            logger.error(f'[creating campaign by medium failed]-[medium: {medium}]-[exc: {e}]')
            return

        # create scheduled campaigns
        schedules = CampaignSchedule.objects.filter(
            campaign_id__in=campaigns.values_list('id', flat=True),
            week_day=timezone.now().date().weekday(),
            start_time__lte=timezone.now().time(),
            end_time__gt=timezone.now().time(),
        )

        for schedule in schedules:
            schedule_lower_range = timezone.now().replace(
                hour=schedule.start_time.hour,
                minute=schedule.start_time.minute,
            )

            schedule_upper_range = timezone.now().replace(
                hour=schedule.end_time.hour,
                minute=schedule.end_time.minute,
            )

            create_campaign_func(schedule.campaign, schedule_lower_range, schedule_upper_range)

        # create non scheduled campaigns if possible
        concurrent_campaign_count = CampaignReference.objects.live().count()
        if concurrent_campaign_count < settings.ADBOT_MAX_CONCURRENT_CAMPAIGN:
            campaigns = campaigns.filter(
                schedules__isnull=True
            ).annotate(
                num_ref=Count('campaignreference')
            ).order_by('num_ref')
            for campaign in campaigns[:settings.ADBOT_MAX_CONCURRENT_CAMPAIGN - concurrent_campaign_count]:
                start_datetime = timezone.now()
                end_datetime = start_datetime + timedelta(hours=18)

                create_campaign_func(campaign, start_datetime, end_datetime)
