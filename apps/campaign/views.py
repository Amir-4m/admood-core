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
