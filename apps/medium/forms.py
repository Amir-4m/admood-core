from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from apps.medium.models import Publisher, Category, CostModelPrice


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.filter(medium=self.instance.medium)
        self.fields['cost_models'].queryset = CostModelPrice.objects.filter(medium=self.instance.medium)

    def clean(self):
        status = self.cleaned_data.get('status')
        # to approving the status of publisher cost_models field could not be empty
        if not self.cleaned_data.get('cost_models') and status == Publisher.STATUS_APPROVED:
            raise ValidationError({'status': _("to approve the publisher, cost models can not be empty.")})

        # validating publisher medium and category medium be same
        for category in self.cleaned_data.get('categories', []):
            if category.medium != self.instance.medium:
                raise ValidationError({'categories': _("category's medium doesn't match with publisher's medium.")})
        return self.cleaned_data


