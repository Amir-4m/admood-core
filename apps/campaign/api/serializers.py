from rest_framework import serializers

from apps.campaign.models import Province, Campaign, CampaignTargetDevice, CampaignContent


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class TargetDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTargetDevice
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignContent
        fields = '__all__'
