import requests
from celery import shared_task

from admood_core.settings import ADBOT_API_URL, ADBOT_API_TOKEN
from apps.medium.consts import Medium
from apps.medium.models import Publisher


@shared_task
def update_telegram_publishers():
    headers = {'Authorization': ADBOT_API_TOKEN, }
    channels_url = f'{ADBOT_API_URL}/api/v1/channels/'
    r = requests.get(url=f'{channels_url}', headers=headers)
    if not r.ok:
        return
    data = r.json()
    for channel in data:
        Publisher.objects.create(
            reference_id=channel['id'],
            medium=Medium.TELEGRAM,
            name=channel['title'],
            is_enable=channel['is_enable']
        )
