from rest_framework import serializers
from ..models import Device, Platform, OS, Version


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


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
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = instance[0]
        data["title"] = instance[1]
        return data
