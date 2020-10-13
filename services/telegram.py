import json

import requests
from rest_framework.status import HTTP_400_BAD_REQUEST

from admood_core.settings import ADBOT_API_TOKEN, ADBOT_API_URL
from services.utils import file_type

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
    publishers = campaign.campaignpublisher_set.select_related('publisher').values_list(
        'publisher__ref_id', 'publisher_price'
    )

    data = dict(
        title=campaign.name,
        status=status,
        is_enable=False,
        publishers=list(publishers),
        max_view=campaign.remaining_views,
        agents=campaign.extra_data.get('agents', []),
        start_datetime=start_time,
        end_datetime=end_time,
    )
    try:
        r = requests.post(url=CAMPAIGN_URL, headers=JSON_HEADERS, data=json.dumps(data))
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e

    return r.json()['id']


def create_content(content, campaign_id):
    data = dict(
        campaign=campaign_id,
        display_text=content.title,
        content=content.data.get('content'),
        links=content.data.get('links', []) or [],
        inlines=content.data.get('inlines', []) or [],
        is_sticker=content.data.get('is_sticker', False),
        mother_channel=content.data.get('mother_channel', None),
        view_type=content.data.get('view_type'),
    )
    try:
        r = requests.post(url=CONTENT_URL, headers=JSON_HEADERS, data=json.dumps(data))
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e

    return r.json()['id']


def create_file(file, content_id, telegram_file_hash=None):
    data = dict(
        name=file.name,
        file_type=file_type(file.name),
        campaign_content=content_id,
        telegram_file_hash=telegram_file_hash
    )
    try:
        if telegram_file_hash:
            r = requests.post(url=FILE_URL, headers=HEADERS, data=data)
        else:
            r = requests.post(url=FILE_URL, headers=HEADERS, data=data, files={'file': file})
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return True


def enable_campaign(campaign_id):
    try:
        r = requests.patch(url=f'{CAMPAIGN_URL}{campaign_id}/', headers=HEADERS, data={'is_enable': True})
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return True


def campaign_report(campaign_id):
    try:
        r = requests.get(url=f'{CAMPAIGN_URL}{campaign_id}/report', headers=HEADERS)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return r.json()


def get_publishers():
    headers = {'Authorization': ADBOT_API_TOKEN, }
    channels_url = f'{ADBOT_API_URL}/api/v1/channels/'
    try:
        r = requests.get(url=f'{channels_url}', headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return r.json()


def get_campaign(campaign_id):
    try:
        r = requests.get(url=f'{CAMPAIGN_URL}{campaign_id}/', headers=HEADERS)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return r.json()


def get_contents(campaign_id):
    campaign = get_campaign(campaign_id)
    contents = campaign.get('contents', None)
    return contents


def test_campaign(campaign_id):
    try:
        r = requests.get(url=f'{CAMPAIGN_URL}{campaign_id}/test/', headers=HEADERS, timeout=120)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e

    return r.json()["detail"]
