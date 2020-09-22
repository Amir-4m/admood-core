from celery import shared_task

from apps.medium.consts import Medium
from apps.medium.models import Publisher
from services.telegram import get_publishers


@shared_task
def update_telegram_publishers():
    channels = get_publishers()
    for channel in channels:
        Publisher.objects.update_or_create(
            reference_id=channel['id'],
            medium=Medium.TELEGRAM,
            defaults={
                'name': channel['title'],
                'is_enable': channel['is_enable']
            }
        )
