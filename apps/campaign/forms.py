from django import forms
from django.core.exceptions import ValidationError

from django_admin_json_editor import JSONEditorWidget

from apps.campaign.models import CampaignContent, Campaign
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

DATA_SCHEMA_CAMPAIGN = {
    'type': 'object',
    'title': 'extra data',
    'properties': {
        'post_limit': {
            'title': 'Post Limit',
            'type': 'integer',
            'format': 'integer',
        }
    },
}


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
        fields = "__all__"
        widgets = {
            'extra_data': JSONEditorWidget(schema=DATA_SCHEMA_CAMPAIGN),
        }

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
            valid, msg_err = self.instance.approve_validate(status=status)
            if not valid:
                raise ValidationError({'status': msg_err})

        return self.cleaned_data
