from django.utils import timezone

from apps.campaign.services import TelegramCampaignServices


def update_campaign_reference_adtel(campaign_ref):
    """
        Updating `views`, `detail` and hourly report of the campaign reference object from ad-tel.
    """
    # y => value, label => hour
    key_value_list_gen = lambda data: [dict(y=data[key], name=key) for key in data.keys()]

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


def get_hourly_report_dashboard(temp_reports, sort_key):
    """
        "temp_reports" is a object that contains:
        { "name": 15, "y": 52, "y-cost": 52000, "cr-date": datetime.datetime(2021, 2, 14, 16, 55) }
        `y`=> views
        `y-cost`=> views * cost_model_price of content
        `name`=> time of report
        `cr-date`=> start time of campaign reference `campaign_reference.schedule_range.lower`
         ``
        These reports after calculating changes to blow.
        report object contains the cost and view data like this
        report => { "17": [ [4, 5], [4000, 5000] ] }
        collecting all values for each time and sum of this become the result for view chart and cost chart
    """
    chart = {}
    cost_chart = []
    view_chart = []

    for rep in temp_reports:
        if rep[sort_key] in chart:
            chart[f'{rep[sort_key]}'][0].append(rep['y'])
            chart[f'{rep[sort_key]}'][1].append(rep['y-cost'])
        else:
            chart[f'{rep[sort_key]}'] = [[rep['y']], [rep['y-cost']]]
    keys = chart.keys()
    # calculating the view chart
    for key in keys:
        view_chart.append({"name": f'{key}', "y": sum(chart[key][0])})

    # calculating the cost chart
    for key in keys:
        cost_chart.append({"name": f'{key}', "y": sum(chart[key][1])})

    return cost_chart, view_chart
