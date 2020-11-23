from datetime import datetime

from rest_framework import serializers

from apps.core.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

    def create(self, validated_data):
        file = validated_data['file']
        ext = file.name.split('.')[-1]
        file.name = f"{datetime.now().strftime('%Y-%m-%d')}_{self.context['request'].user.username}.{ext}"
        return super(FileSerializer, self).create(validated_data)
