import json

import requests
from rest_framework.status import HTTP_400_BAD_REQUEST

from admood_core.settings import ADBOT_API_TOKEN, ADBOT_API_URL
from apps.core.consts import CostModel
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
    publishers = []
    for publisher in campaign.final_publishers.all():
        try:
            publisher_price = publisher.cost_models.get(publisher=publisher, cost_model=CostModel.CPV).publisher_price
        except:
            publisher_price = 0
        publishers.append((publisher.ref_id, publisher_price))

    data = dict(
        title=campaign.name,
        status=status,
        is_enable=False,
        publishers=publishers,
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
            if not link.get('utm_term', None):
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
    try:
        r = requests.post(url=CONTENT_URL, headers=JSON_HEADERS, data=json.dumps(data))
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e

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
    try:
        if telegram_file_hash:
            r = requests.post(url=FILE_URL, headers=HEADERS, data=data)
        else:
            r = requests.post(url=FILE_URL, headers=HEADERS, data=data, files={'file': file})
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e


def enable_campaign(campaign_id):
    try:
        r = requests.patch(url=f'{CAMPAIGN_URL}{campaign_id}/', headers=HEADERS, data={'is_enable': True})
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e
    return True


def campaign_report(campaign_id):
    try:
        r = requests.get(url=f'{CAMPAIGN_URL}{campaign_id}/report', headers=HEADERS)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e
    return r.json()


def get_publishers():
    headers = {'Authorization': ADBOT_API_TOKEN, }
    channels_url = f'{ADBOT_API_URL}/api/v1/channels/'
    try:
        r = requests.get(url=f'{channels_url}', headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
    except requests.exceptions.RequestException as e:
        raise e
    return r.json()


def get_campaign(campaign_id):
    try:
        r = requests.get(url=f'{CAMPAIGN_URL}{campaign_id}/', headers=HEADERS)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(e.response.text)
        raise e
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
