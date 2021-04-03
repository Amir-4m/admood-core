import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.campaign.models import Campaign
from apps.medium.consts import Medium

from .services import TelegramCampaignServices

logger = logging.getLogger(__name__)


def test_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.medium == Medium.TELEGRAM:

        # validating the extra_data field
        telegram_require_campaign_extra_data = ['post_limit']
        extra_data_keys = campaign.extra_data.keys()
        has_error = False

        for key in telegram_require_campaign_extra_data:
            if key not in extra_data_keys:
                has_error = True
                messages.error(request, _(f'this value ({key}) is required on extra_data field.'))

        # validating the mother_channel on data field of campaign's contents
        # mother_channel is required for CampaignContent.data JSON field on telegram medium
        for content in campaign.contents.all():
            if not content.data.get('mother_channel', None):
                has_error = True
                messages.error(
                    request,
                    _(f'(mother_channel) field is required or has a invalid data. please check it on (data) field on '
                      f'campaign content {content.id}.')
                )

        # create telegram campaign if has no error
        if not has_error:
            try:
                result = TelegramCampaignServices.create_telegram_test_campaign(campaign)
            except Exception as e:
                logger.error(f"[testing campaign failed]-[campaign id: {campaign.id}]-[exc: {e}]")
                messages.error(request, _(e.__str__()))
            else:
                messages.info(request, _("The test was performed correctly."))
    else:
        messages.warning(request, _("Currently only Telegram medium can be tested."))

    return HttpResponseRedirect(reverse("admin:campaign_campaign_change", args=(pk,)))
