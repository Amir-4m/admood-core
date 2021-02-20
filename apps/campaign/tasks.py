from celery.schedules import crontab
from celery.task import periodic_task
import logging

from django.utils import timezone
from django.db import transaction
from django.conf import settings

from apps.campaign.models import Campaign, CampaignReference, CampaignContent
from apps.medium.consts import Medium
from apps.payments.models import Transaction

from .services import CampaignService, TelegramCampaignServices

logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute="*"))
def disable_finished_campaigns():
    campaigns = Campaign.objects.select_for_update(skip_locked=True).filter(
        is_enable=True,
        status=Campaign.STATUS_APPROVED,
        start_date__lte=timezone.now().date(),
    )

    # disable expired and over budget campaigns
    with transaction.atomic():
        for campaign in campaigns:
            if campaign.is_finished():
                # create a deduct transaction
                Transaction.objects.create(
                    user=campaign.owner,
                    value=campaign.total_cost,
                    campaign=campaign,
                    transaction_type=Transaction.TYPE_DEDUCT,
                )
                campaign.is_enable = False
                campaign.save()


@periodic_task(run_every=crontab(**settings.CREATE_TELEGRAM_CAMPAIGN_TASK_CRONTAB))
def create_telegram_campaign_task():
    # filter approved and enable telegram campaigns
    campaigns = Campaign.objects.live().filter(medium=Medium.TELEGRAM, error_count__lt=5)
    CampaignService.create_campaign_by_medium(campaigns, 'telegram')


# update content view in Campaign Reference model and add telegram file hashes
@periodic_task(run_every=crontab(**settings.UPDATE_TELEGRAM_INFO_TASK_CRONTAB))
def update_telegram_info_task():
    # filter appropriate campaigns to save gotten views
    campaign_refs = CampaignReference.objects.monitor_report()

    for campaign_ref in campaign_refs:
        update_campaign_reference_adtel(campaign_ref)

        camp = campaign_ref.campaign
        # getting file hashes for the first campaign reference is enough
        if camp.campaignreference_set.count() == 1:
            for content in campaign_ref.contents:
                content_id = content["content"]
                for item in TelegramCampaignServices().get_contents(campaign_ref.ref_id):
                    if item["id"] == content["ref_id"]:
                        c = CampaignContent.objects.get(pk=content_id)
                        for file in item["files"]:
                            c.data["telegram_file_hash"] = file["telegram_file_hash"]
                            c.save()
                            # currently one file can be saved
                            break


def update_campaign_reference_adtel(campaign_ref):
    # y => value, label => hour
    key_value_list_gen = lambda data: [dict(y=data[key], label=key) for key in sorted(data.keys())]

    # store telegram file hash of screenshot in TelegramCampaign model
    campaign_ref.campaign.telegramcampaign.telegram_file_hash = TelegramCampaignServices().campaign_telegram_file_hash(
        campaign_ref.ref_id)
    # get each content views and store in content json field
    reports = TelegramCampaignServices().campaign_report(campaign_ref.ref_id)
    for content in campaign_ref.contents:
        for report in reports:
            if content["ref_id"] == report["content"]:
                content["views"] = report["views"]
                content["detail"] = report["detail"]

                if 'hourly' in report.keys():
                    content['graph_hourly_cumulative'] = key_value_list_gen(report['hourly'])
                    content['graph_hourly_view'] = {}
                    # creating the view by hour
                    keys = sorted(report['hourly'].keys(), reverse=True)
                    if keys:
                        for index, key in enumerate(keys, 0):
                            if index + 1 == len(keys):
                                content['graph_hourly_view'][keys[index]] = report['hourly'][keys[index]]
                            else:
                                content['graph_hourly_view'][key] = report['hourly'][key] - report['hourly'][
                                    keys[index + 1]]
                        content['graph_hourly_view'] = key_value_list_gen(content['graph_hourly_view'])

                    # end of getting report for this campaign
                    # TODO telegram issue - If telegram can't read new reports on end time of campaign reference
                    end_time_campaign = campaign_ref.schedule_range.upper
                    if timezone.now() > end_time_campaign and end_time_campaign.hour in report['hourly'].keys():
                        campaign_ref.report_time = timezone.now()

    campaign_ref.save()


# TODO create_instagram_campaign_task is disable for now
# @periodic_task(run_every=crontab())
# def create_instagram_campaign_task():
#     campaigns = Campaign.objects.live().filter(
#         Q(medium=Medium.INSTAGRAM_POST) |
#         Q(medium=Medium.INSTAGRAM_STORY),
#         error_count__lt=5
#     )
#     CampaignService.create_campaign_by_medium(campaigns, 'instagram')
