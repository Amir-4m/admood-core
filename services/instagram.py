import json

from admood_core.settings import ADINSTA_API_TOKEN, ADINSTA_API_URL
from services.utils import file_type, custom_request

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


def create_insta_campaign(campaign, start_time, end_time, status):
    publishers = campaign.final_publishers.select_related('publisher').values_list(
        'publisher__ref_id', 'publisher_price'
    )

    data = dict(
        title=campaign.name,
        status=status,
        is_enable=False,
        publishers=list(publishers),
        campaign_type=campaign.get_medium_display().split('_')[1],
        start_datetime=start_time,
        end_datetime=end_time,
    )
    r = custom_request(url=CAMPAIGN_URL, headers=JSON_HEADERS, data=json.dumps(data))
    return r.json()['id']


def create_insta_content(content, campaign_id):
    data = dict(
        campaign=campaign_id,
        title=content.title,
        caption=content.data.get('content'),
        description=content.description
    )
    r = custom_request(url=CONTENT_URL, headers=JSON_HEADERS, data=json.dumps(data))
    return r.json()['id']


def create_insta_media(file, content_id):
    data = dict(
        file_type=file_type(file.name),
        content=content_id,
    )
    custom_request(url=MEDIA_URL, headers=HEADERS, data=data, files={'file': file})


def enable_Insta_campaign(campaign_id):
    custom_request(url=f'{CAMPAIGN_URL}{campaign_id}/', method='patch', headers=HEADERS, data={'is_enable': True})
    return True


def get_insta_publishers():
    headers = {'Authorization': ADINSTA_API_TOKEN}
    pages_url = f'{ADINSTA_API_URL}/api/v1/instagram/pages/'
    r = custom_request(url=f'{pages_url}', method='get', headers=headers)
    return r.json()


def get_insta_campaign(campaign_id):
    r = custom_request(url=f'{CAMPAIGN_URL}{campaign_id}/', method='get', headers=HEADERS)
    return r.json()


def get_contents(campaign_id):
    campaign = get_insta_campaign(campaign_id)
    contents = campaign.get('contents', None)
    return contents

