import datetime

from rest_framework import serializers

from apps.campaign.models import Province, Campaign, CampaignContent, CampaignSchedule, TargetDevice


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class CampaignScheduleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CampaignSchedule
        fields = ('id', 'day', 'start_time', 'end_time')

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError(
                {'end_time': 'end_time should be greater than start_time'},
            )
        return attrs


class TargetDeviceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = TargetDevice
        fields = ('id', 'device', 'service_provider')


class CampaignSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(allow_null=True)
    targetdevice_set = TargetDeviceSerializer(many=True)
    campaignschedule_set = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['owner', 'status']

    def validate(self, attrs):

        medium = attrs.get('medium')
        publishers = attrs.get('publishers', [])
        categories = attrs.get('categories', [])

        if publishers == categories is None:
            raise serializers.ValidationError("Publishers and categories both can not be empty")

        for category in categories:
            if category.medium != medium:
                raise serializers.ValidationError("Campaign's medium and category's medium must be the same.")

        for publisher in publishers:
            if publisher.medium != medium:
                raise serializers.ValidationError("Campaign's medium and publisher's medium must be the same.")

        schedule_set = attrs.get('campaignschedule_set', [])[:]
        while schedule_set:
            schedule = schedule_set.pop()
            for i in schedule_set:
                if schedule['day'] == i['day']:
                    if not (
                            (schedule['start_time'] < i['start_time'] and schedule['end_time'] < i['start_time']) or
                            (schedule['start_time'] > i['end_time'] and schedule['end_time'] > i['end_time'])
                    ):
                        raise serializers.ValidationError(
                            {'campaignschedule_set': 'invalid schedule start_time or end_time'})

        return attrs

    def create(self, validated_data):
        targetdevice_set = validated_data.pop("targetdevice_set", [])
        schedule_set = validated_data.pop("campaignschedule_set", [])

        if validated_data['start_date'] is None:
            validated_data["start_date"] = datetime.date.today()

        campaign = super().create(validated_data)

        for targetdevice_data in targetdevice_set:
            TargetDevice.objects.create(campaign=campaign, **targetdevice_data)

        for schedule_data in schedule_set:
            CampaignSchedule.objects.create(campaign=campaign, **schedule_data)

        return campaign

    def update(self, instance, validated_data):
        targetdevice_set = validated_data.pop("targetdevice_set")
        schedule_set = validated_data.pop("campaignschedule_set")

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


class CampaignEnableSerializer(serializers.ModelSerializer):
    is_enable = serializers.BooleanField(required=True)

    class Meta:
        model = Campaign
        fields = ["is_enable"]


class CampaignContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignContent
        fields = '__all__'
        read_only_fields = ['campaign']
