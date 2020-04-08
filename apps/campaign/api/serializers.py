from rest_framework import serializers

from apps.campaign.models import Province, Campaign, Device, Content, Schedule, TargetDevice


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('type', 'title', 'parent')


class CampaignScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('day', 'start_time', 'end_time')


class TargetDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetDevice
        fields = ('device', 'service_provider')


class CampaignSerializer(serializers.ModelSerializer):
    targetdevice_set = TargetDeviceSerializer(many=True)
    schedule_set = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['status']

    def create(self, validated_data):
        targetdevice_set = validated_data.pop("targetdevice_set")
        schedule_set = validated_data.pop("schedule_set")
        campaign = super().create(validated_data)

        for targetdevice_data in targetdevice_set:
            TargetDevice.objects.create(campaign=campaign, **targetdevice_data)

        for schedule_data in schedule_set:
            Schedule.objects.create(campaign=campaign, **schedule_data)

        return campaign


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'
