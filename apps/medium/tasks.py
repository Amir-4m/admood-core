from django.conf import settings

from celery.task import periodic_task
from celery.schedules import crontab

from apps.campaign.services import InstagramCampaignServices, TelegramCampaignServices
from apps.medium.consts import Medium
from apps.medium.models import Publisher


@periodic_task(run_every=crontab(**settings.UPDATE_TELEGRAM_PUBLISHERS_TASK_CRONTAB))
def update_telegram_publishers_task():
    channels = TelegramCampaignServices().get_publishers()
    for channel in channels:
        Publisher.objects.update_or_create(
            ref_id=channel['id'],
            medium=Medium.TELEGRAM,
            defaults={
                'name': channel['title'],
                'extra_data': {
                    'member_no': channel['member_no'],
                    'view_efficiency': channel['view_efficiency'],
                    'tag': channel['tag']
                }
            }
        )


# TODO Instagram disable for now
# @shared_task
# def update_instagram_publishers():
#     pages = InstagramCampaignServices().get_insta_publishers()
#     for page in pages:
#         if page['medium'] is None:
#             # update or create publisher for both post and story
#             Publisher.objects.update_or_create(
#                 ref_id=page['id'],
#                 medium=Medium.INSTAGRAM_STORY,
#                 defaults={
#                     'name': page['insta_username'],
#                 }
#             )
#
#             Publisher.objects.update_or_create(
#                 ref_id=page['id'],
#                 medium=Medium.INSTAGRAM_POST,
#                 defaults={
#                     'name': page['insta_username'],
#                 }
#             )
#         else:
#             Publisher.objects.update_or_create(
#                 ref_id=page['id'],
#                 medium=page['medium'],
#                 defaults={
#                     'name': page['insta_username'],
#                 }
#             )
