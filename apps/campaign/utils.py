from django.utils import timezone

from apps.campaign.services import TelegramCampaignServices


def update_campaign_reference_adtel(campaign_ref):
    # y => value, label => hour
    key_value_list_gen = lambda data: [dict(y=data[key], name=key) for key in sorted(data.keys())]

    # store telegram file hash of screenshot in TelegramCampaign model
    file_hash = TelegramCampaignServices().campaign_telegram_file_hash(campaign_ref.ref_id)
    if file_hash:
        campaign_ref.campaign.telegramcampaign.telegram_file_hash = file_hash

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
                                content['graph_hourly_view'][key] = abs(report['hourly'][key] - report['hourly'][keys[index + 1]])
                        content['graph_hourly_view'] = key_value_list_gen(content['graph_hourly_view'])

                    # end of getting report for this campaign
                    # TODO telegram issue - If telegram can't read new reports on end time of campaign reference
                    end_time_campaign = campaign_ref.schedule_range.upper
                    if timezone.now() > end_time_campaign and end_time_campaign.hour in report['hourly'].keys():
                        campaign_ref.report_time = timezone.now()

    campaign_ref.save()
