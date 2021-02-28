from rest_framework import serializers
from ..models import Publisher, Category


class MediumSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = instance[0]
        data["title"] = instance[1]
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'display_text']


class PublisherSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Publisher
        fields = '__all__'


class MinorPublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        fields = ('id', 'name')

