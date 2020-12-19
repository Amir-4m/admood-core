from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django_json_widget.widgets import JSONEditorWidget
from django.utils.safestring import mark_safe

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


class ContentLinkWidget(forms.Widget):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(ContentLinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if self.object.pk:
            content_links = []
            for content in self.object.contents.filter(is_hidden=False):
                content_links.append(
                    f'<a target="_blank" href="{reverse(f"admin:{content._meta.app_label}_{content._meta.model_name}_change", kwargs={"object_id": content.id})}">{content.title}</a>',
                )
            return mark_safe(
                ', '.join(content_links)
            )
        else:
            return mark_safe(u'')


class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = CampaignContent
        fields = '__all__'
        widgets = {
            'data': JSONEditorWidget,
        }


class CampaignAdminForm(forms.ModelForm):
    daily_budget = forms.IntegerField(localize=True)
    total_budget = forms.IntegerField(localize=True)
    contents = forms.CharField(required=False)

    class Meta:
        model = Campaign
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        final_publishers = Publisher.objects.filter(
            is_enable=True,
            status=Publisher.STATUS_APPROVED,
        )
        if self.instance.medium:
            final_publishers = final_publishers.filter(medium=self.instance.medium)
        if self.instance:
            self.fields['contents'].widget = ContentLinkWidget(self.instance)
        self.fields['final_publishers'].queryset = final_publishers

    def clean(self):
        if self.instance:
            if self.instance.medium == Medium.TELEGRAM:
                status = self.cleaned_data.get('status')
                if status == Campaign.STATUS_APPROVED:
                    if hasattr(self.instance, 'telegramcampaign'):
                        return self.cleaned_data
                    raise ValidationError({'status': 'to approve the campaign upload the test screenshot.'})
        return self.cleaned_data
