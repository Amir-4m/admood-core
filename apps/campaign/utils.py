from pprint import pprint

from django.utils import timezone


def sort_hours(start_date, end_date):
    diff = end_date - start_date
    days, seconds = diff.days, diff.seconds
    diff_hours = (days * 24 + seconds // 3600) + 1
    hour = start_date.hour

    sorted_hours = []
    for i in range(diff_hours):
        sorted_hours.append(str(hour))
        hour += 1
        if hour >= 24:
            hour = 0
    return sorted_hours


def sort_reports_by_hour(data, start_date, end_date):
    """Sort reports by campaign reference start date"""
    if len(data) <= 1:
        return [dict(y=data[key], name=key) for key in data.keys()]
    result = []
    keys = data.keys()

    # y => value, label => hour
    for key in sort_hours(start_date, end_date):
        if key in keys:
            result.append(dict(y=data[key], name=key))
    return result


def update_campaign_reference_adtel(campaign_ref):
    from apps.campaign.services import TelegramCampaignServices

    """
        Updating `views`, `detail` and hourly report of the campaign reference object from ad-tel.
    """
    # store telegram file hash of screenshot in TelegramCampaign model
    file_hash = TelegramCampaignServices().campaign_telegram_file_hash(campaign_ref.ref_id)
    if file_hash:
        campaign_ref.campaign.telegramcampaign.telegram_file_hash = file_hash

    # get each content views and store in content json field
    reports = TelegramCampaignServices().campaign_report(campaign_ref.ref_id)
    for content in campaign_ref.contents:
        for report in reports:
            if content["ref_id"] == report["content"]:
                start_date = campaign_ref.schedule_range.lower
                end_date = campaign_ref.schedule_range.upper

                content["views"] = report["views"]
                content["detail"] = report["detail"]

                if 'hourly' in report.keys():
                    # hourly cumulative
                    content['graph_hourly_cumulative'] = sort_reports_by_hour(report['hourly'], start_date, end_date)

                    content['graph_hourly_view'] = {}
                    # creating the view by hour
                    keys = sort_hours(start_date, end_date)
                    for index, key in enumerate(keys, 0):
                        try:
                            if index + 1 == len(report['hourly']):
                                content['graph_hourly_view'][key] = report['hourly'][key]
                            else:
                                content['graph_hourly_view'][keys[index + 1]] = abs(report['hourly'][key] - report['hourly'][keys[index + 1]])
                                if index == 0:
                                    content['graph_hourly_view'][key] = report['hourly'][key]
                        except:
                            continue
                    content['graph_hourly_view'] = sort_reports_by_hour(
                        content['graph_hourly_view'], start_date, end_date
                    )
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


def compute_telegram_cost(views, cost_model_price):
    return int(views / 1000 * cost_model_price)
