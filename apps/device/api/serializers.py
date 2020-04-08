from rest_framework import serializers
from ..models import Platform, OS, Version


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'


class OSSerializer(serializers.ModelSerializer):
    class Meta:
        model = OS
        fields = '__all__'


class OSVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'


class ProviderSerializer(serializers.Serializer):
    child = serializers.ListField(child=serializers.CharField())
