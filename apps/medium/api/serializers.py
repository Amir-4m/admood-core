from rest_framework import serializers
from ..models import Publisher, MediumCategory


class MediumSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = instance[0]
        data["title"] = instance[1]
        return data


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class MediumCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MediumCategory
        fields = ['display_text', 'id']
