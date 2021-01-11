import logging
import json

from admood_core.settings import ADBOT_API_TOKEN, ADBOT_API_URL, ADBOT_AGENTS
from apps.core.consts import CostModel
from services.utils import file_type, custom_request

logger = logging.getLogger(__name__)

JSON_HEADERS = {
    'Authorization': ADBOT_API_TOKEN,
    'Content-type': 'application/json'
}
HEADERS = {
    'Authorization': ADBOT_API_TOKEN,
}

CAMPAIGN_URL = f'{ADBOT_API_URL}/api/v1/campaigns/'
CONTENT_URL = f'{ADBOT_API_URL}/api/v1/contents/'
FILE_URL = f'{ADBOT_API_URL}/api/v1/files/'


def create_campaign(campaign, start_time, end_time, status):
    publishers = []
    for publisher in campaign.final_publishers.all():
        try:
            publisher_price = publisher.cost_models.filter(
                cost_model=CostModel.CPV
            ).order_by('-publisher_price').first().publisher_price
        except:
            publisher_price = 0
        publishers.append((publisher.ref_id, publisher_price))

    data = dict(
        title=campaign.name,
        status=status,
        is_enable=False,
        publishers=publishers,
        max_view=campaign.remaining_views,
        agents=campaign.extra_data.get('agents', [ADBOT_AGENTS]) if campaign.extra_data else [ADBOT_AGENTS],
        start_datetime=start_time.__str__(),
        end_datetime=end_time.__str__(),
    )

    r = custom_request(url=CAMPAIGN_URL, headers=JSON_HEADERS, json=data)
    return r.json()['id']


def create_content(content, campaign_id):
    if 'post_link' in content.data:
        data = dict(
            campaign=campaign_id,
            display_text=content.title,
            post_link=content.data.get('post_link'),
            view_type=content.data.get('view_type'),
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

    r = custom_request(url=CONTENT_URL, headers=JSON_HEADERS, data=json.dumps(data))
    return r.json()['id']


def create_file(file, campaign_id=None, content_id=None, telegram_file_hash=None):
    data = dict(
        name=file.name,
        file_type=file_type(file.name),
        telegram_file_hash=telegram_file_hash
    )
    if campaign_id:
        data['campaign'] = campaign_id
    if content_id:
        data['campaign_content'] = content_id

    if telegram_file_hash:
        custom_request(url=FILE_URL, headers=HEADERS, data=data)
    else:
        custom_request(url=FILE_URL, headers=HEADERS, data=data, files={'file': file})


def enable_campaign(campaign_id):
    r = custom_request(url=f'{CAMPAIGN_URL}{campaign_id}/', method='patch', headers=HEADERS, data={'is_enable': True})
    return True


def campaign_report(campaign_id):
    r = custom_request(url=f'{CAMPAIGN_URL}{campaign_id}/report', method='get', headers=HEADERS)
    return r.json()


def get_publishers():
    headers = {'Authorization': ADBOT_API_TOKEN, }
    channels_url = f'{ADBOT_API_URL}/api/v1/channels/'
    r = custom_request(url=f'{channels_url}', method='get', headers=headers)
    return r.json()


def get_campaign(campaign_id):
    r = custom_request(url=f'{CAMPAIGN_URL}{campaign_id}/', method='get', headers=HEADERS)
    return r.json()


def get_contents(campaign_id):
    campaign = get_campaign(campaign_id)
    contents = campaign.get('contents', None)
    return contents


def campaign_telegram_file_hash(campaign_id):
    campaign = get_campaign(campaign_id)
    file = campaign.get('file')['telegram_file_hash']
    return file


def test_campaign(campaign_id):
    r = custom_request(url=f'{CAMPAIGN_URL}{campaign_id}/test/', method='get', headers=HEADERS, timeout=120)
    return r.json()["detail"]
