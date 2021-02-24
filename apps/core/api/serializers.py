from django.utils import timezone
from rest_framework import serializers

from apps.core.models import File
from services.utils import random_string


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

    def create(self, validated_data):
        file = validated_data['file']
        ext = file.name.split('.')[-1]
        file.name = f"{timezone.now().strftime('%Y-%m-%d-%H-%-M-%-S')}_{random_string(length=3)}.{ext}"
        return super(FileSerializer, self).create(validated_data)
