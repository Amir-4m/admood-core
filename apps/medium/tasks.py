from celery import shared_task

from apps.medium.consts import Medium
from apps.medium.models import Publisher
from services.telegram import get_publishers
from services.instagram import get_insta_publishers


@shared_task
def update_telegram_publishers():
    channels = get_publishers()
    for channel in channels:
        Publisher.objects.update_or_create(
            ref_id=channel['id'],
            medium=Medium.TELEGRAM,
            defaults={
                'name': channel['title'],
            }
        )


@shared_task
def update_instagram_publishers():
    pages = get_insta_publishers()
    for page in pages:
        if page['medium'] is None:
            # update or create publisher for both post and story
            Publisher.objects.update_or_create(
                ref_id=page['id'],
                medium=Medium.INSTAGRAM_STORY,
                defaults={
                    'name': page['insta_username'],
                }
            )

            Publisher.objects.update_or_create(
                ref_id=page['id'],
                medium=Medium.INSTAGRAM_POST,
                defaults={
                    'name': page['insta_username'],
                }
            )
        else:
            Publisher.objects.update_or_create(
                ref_id=page['id'],
                medium=page['medium'],
                defaults={
                    'name': page['insta_username'],
                }
            )
