from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.campaign.models import Campaign, CampaignReference
from apps.campaign.telegram.telegram import create_telegram_test_campaign
from apps.medium.consts import Medium
from apps.medium.models import Publisher


def test_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.medium == Medium.TELEGRAM:
        try:
            result = create_telegram_test_campaign(campaign)
        except Exception as e:
            messages.error(request, _(e.__str__()))
        else:
            if result is True:
                messages.info(request, _("The test was performed correctly."))
            else:
                messages.info(request, _(result))
    else:
        messages.warning(request, _("Currently only Telegram medium can be tested."))
    return HttpResponseRedirect(reverse("admin:campaign_campaign_change", args=(pk,)))


def export_campaign_report_csv(request, pk):
    try:
        campaign_ref = CampaignReference.objects.get(pk=pk)
    except CampaignReference.DoesNotExist:
        raise Http404('not found!')
    publishers_detail = []
    if campaign_ref.campaign.medium == Medium.TELEGRAM:
        for content in campaign_ref.contents:
            for detail in content['detail']:
                publishers_detail.append({
                    'publishers': Publisher.objects.filter(ref_id__in=detail['channel_ids']).values('name',
                                                                                                    'extra_data__tag'),
                    'posts': detail['posts']

                })
    response = render(request, 'campaign/export_csv.html', {
        'publishers_detail': publishers_detail,
    }, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{campaign_ref.date}-{campaign_ref.start_time}.xls"'
    return response
