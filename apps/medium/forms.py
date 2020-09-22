from django import forms
from django.core.exceptions import ValidationError

from apps.medium.models import Publisher


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = '__all__'

    def clean(self):
        categories = self.cleaned_data.get('categories', [])
        medium = self.cleaned_data.get('medium', None)

        for category in categories:
            if category.medium != medium:
                raise ValidationError({'categories': "category's medium doesn't match with publisher's medium."})
        return self.cleaned_data
