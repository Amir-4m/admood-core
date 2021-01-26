from django import forms
from django.core.exceptions import ValidationError
from django_admin_json_editor import JSONEditorWidget
from django.utils.translation import ugettext_lazy as _


from apps.campaign.models import CampaignContent, Campaign
from apps.medium.consts import Medium
from apps.medium.models import Publisher


# DATA_SCHEMA = {
#     'type': 'object',
#     'title': 'Data',
#     'properties': {
#         'view_type': {
#             'title': 'view type',
#             'type': 'string',
#             'enum': ['partial', 'total'],
#         },
#         'content': {
#             'title': 'Content',
#             'type': 'string',
#             'format': 'textarea',
#         },
#         'links': {
#             'title': 'links',
#             'type': 'array',
#             "items": {
#                 "title": "link",
#                 "type": "object",
#                 "properties": {
#                     "link": {
#                         "title": "link",
#                         "type": "string",
#                     },
#                     "utmTerm":
#                         {
#                             "title": "utm_term",
#                             "type": ["string", "null"]
#                         }
#                 }
#             }
#         },
#         'file': {
#             'title': 'file',
#             'type': 'integer',
#         },
#         'mother_channel':
#             {
#                 'title': 'mother_channel',
#                 'type': 'integer'
#             }
#     },
# }
#


class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = CampaignContent
        fields = '__all__'
        widgets = {
            'data': JSONEditorWidget(schema={}),
        }


class CampaignAdminForm(forms.ModelForm):
    daily_budget = forms.IntegerField(localize=True)
    total_budget = forms.IntegerField(localize=True)

    class Media:
        js = ('campaign/js/numeral.min.js', 'campaign/js/script.js')

    class Meta:
        model = Campaign
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query_params = dict(
            is_enable=True,
            status=Publisher.STATUS_APPROVED,
            cost_models__isnull=False
        )
        if self.instance.medium:
            query_params['medium'] = self.instance.medium

        # final_publishers = Publisher.objects.filter(**query_params)
        # self.fields['final_publishers'].queryset = final_publishers

    def clean(self):
        if self.instance:
            status = self.cleaned_data.get('status')
            if self.instance.medium == Medium.TELEGRAM:
                if status == Campaign.STATUS_APPROVED and not hasattr(self.instance, 'telegramcampaign'):
                    raise ValidationError({'status': _('to approve the campaign upload the test screenshot.')})

            # if status changed to approved, CampaignContent can not be empty
            if not self.instance.contents.exists() and status == Campaign.STATUS_APPROVED:
                raise ValidationError({'status': _('to approve the campaign, content can not be empty!')})

        return self.cleaned_data
