from django import forms
from django.core.exceptions import ValidationError
from django_admin_json_editor import JSONEditorWidget

from apps.campaign.models import CampaignContent, Campaign
from apps.medium.consts import Medium

DATA_SCHEMA = {
    'type': 'object',
    'title': 'Data',
    'properties': {
        'view_type': {
            'title': 'view type',
            'type': 'string',
            'enum': ['partial', 'total'],
        },
        'content': {
            'title': 'Content',
            'type': 'string',
            'format': 'textarea',
        },
        'links': {
            'title': 'links',
            'type': 'array',
            "items": {
                "title": "link",
                "type": "object",
                "properties": {
                    "link": {
                        "title": "link",
                        "type": "string",
                    },
                    "utmTerm":
                        {
                            "title": "utm_term",
                            "type": ["string", "null"]
                        }
                }
            }
        },
        'file': {
            'title': 'file',
            'type': 'integer',
        },
        'mother_channel':
            {
                'title': 'mother_channel',
                'type': 'integer'
            }
    },
}


class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = CampaignContent
        fields = '__all__'
        widgets = {
            'data': JSONEditorWidget(DATA_SCHEMA, collapsed=False),
        }


class CampaignAdminForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = '__all__'

    def clean(self):
        if self.cleaned_data.get('medium') == Medium.TELEGRAM:
            status = self.cleaned_data.get('status')
            if status == Campaign.STATUS_APPROVED:
                if hasattr(self.instance, 'telegramcampaign'):
                    return self.cleaned_data
                raise ValidationError({'status': 'to approve the campaign upload the test screenshot.'})
        return self.cleaned_data
