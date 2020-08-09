import json
import os

import requests

from admood_core.settings import ADBOT_API_TOKEN
from apps.campaign.telegram import file_type
from apps.campaign.telegram.consts import CAMPAIGN_URL, JSON_HEADERS, HEADERS, CONTENT_URL, FILE_URL
from apps.core.models import File


def create_campaign(campaign):
    data = dict(
        title=campaign.name,
        status="approved",
        view_duration=None,
        is_enable=False,
        owner=1,
        categories=list(campaign.categories.values_list('reference_id', flat=True)),
        channels=list(campaign.publishers.values_list('pk', flat=True)),
        time_slicing=1,
    )
    r = requests.post(url=CAMPAIGN_URL, headers=JSON_HEADERS, data=json.dumps(data))
    if not r.ok:
        return 0

    response = r.json()
    campaign_id = response['id']

    contents = campaign.contents.all()
    for content in contents:
        if not create_content(content, campaign_id):
            return 0

    r = requests.patch(url=f'{CAMPAIGN_URL}{campaign_id}/', headers=HEADERS, data={'is_enable': True})
    if not r.ok:
        return 0
    return campaign_id


def create_content(content, campaign_id):
    data = dict(
        campaign=campaign_id,
        display_text=content.title,
        content=content.data.get('content'),
        tariff_advertiser=content.cost_model_price,
        links=content.data.get('links', []),
        inlines=content.data.get('inlines', []),
        view_type=content.data.get('view_type'),
    )
    r = requests.post(url=CONTENT_URL, headers=JSON_HEADERS, data=json.dumps(data))
    if not r.ok:
        return False

    response = r.json()
    content_id = response['id']

    try:
        file = File.objects.get(pk=int(content.data.get('file'))).file
    except:
        return False

    name, extension = os.path.splitext(file.name)
    data = dict(
        name=file.name,
        file_type=file_type(extension),
        campaign_content=content_id,
    )
    r = requests.post(url=FILE_URL, headers=HEADERS, data=data, files={'file': file})
    if r.ok:
        return True
    return False
