from django.forms import ModelForm
from django_admin_json_editor import JSONEditorWidget

from apps.campaign.models import CampaignContent

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
                "type": "string",
                "properties": {
                    "text": {
                        "type": "string"
                    }
                }
            }
        },
        'file': {
            'title': 'file',
            'type': 'integer',
        },
    },
}


class ContentAdminForm(ModelForm):
    class Meta:
        model = CampaignContent
        fields = '__all__'
        widgets = {
            'data': JSONEditorWidget(DATA_SCHEMA, collapsed=False),
        }
