from django import forms
from django.core.exceptions import ValidationError

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
        categories = self.cleaned_data.get('categories', [])
        medium = self.instance.medium

        for category in categories:
            if category.medium != medium:
                raise ValidationError({'categories': "category's medium doesn't match with publisher's medium."})
        return self.cleaned_data


