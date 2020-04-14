from rest_framework import serializers

from apps.campaign.models import Province, Campaign, Device, CampaignContent, CampaignSchedule, TargetDevice


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('type', 'title', 'parent')


class CampaignScheduleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CampaignSchedule
        fields = ('id', 'day', 'start_time', 'end_time')


class TargetDeviceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = TargetDevice
        fields = ('id', 'device', 'service_provider')


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
            CampaignSchedule.objects.create(campaign=campaign, **schedule_data)

        return campaign

    def update(self, instance, validated_data):
        targetdevice_set = validated_data.pop("targetdevice_set")
        schedule_set = validated_data.pop("schedule_set")

        instance = super().update(instance, validated_data)

        targetdevice_id_list = [i.get("id") for i in targetdevice_set if i.get("id")]
        TargetDevice.objects.filter(campaign=instance).exclude(id__in=targetdevice_id_list).delete()

        schedule_id_list = [i.get("id") for i in schedule_set if i.get("id")]
        CampaignSchedule.objects.filter(campaign=instance).exclude(id__in=schedule_id_list).delete()

        for targetdevice_data in targetdevice_set:
            targetdevice_id = targetdevice_data.get('id', None)
            if targetdevice_id:
                targetdevice = TargetDevice.objects.get(id=targetdevice_id, campaign=instance)
                targetdevice.device = targetdevice_data.get('device', targetdevice.device)
                targetdevice.service_provider = targetdevice_data.get('service_provider', targetdevice.service_provider)
                targetdevice.save()
            else:
                TargetDevice.objects.create(campaign=instance, **targetdevice_data)

        for schedule_data in schedule_set:
            schedule_id = schedule_data.get('id', None)
            if schedule_id:
                schedule = CampaignSchedule.objects.get(id=schedule_id, campaign=instance)
                schedule.day = schedule_data.get('day', schedule.day)
                schedule.start_time = schedule_data.get('start_time', schedule.start_time)
                schedule.end_time = schedule_data.get('end_time', schedule.end_time)
                schedule.save()
            else:
                CampaignSchedule.objects.create(campaign=instance, **schedule_data)

        return instance


class CampaignStatusSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=True)

    class Meta:
        model = Campaign
        fields = ["is_active"]


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignContent
        fields = '__all__'
