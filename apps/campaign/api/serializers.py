import datetime

from rest_framework import serializers, exceptions

from apps.campaign.models import Province, Campaign, CampaignContent, CampaignSchedule, TargetDevice


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class CampaignScheduleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    start_time = serializers.TimeField(default=datetime.time.min)
    end_time = serializers.TimeField(default=datetime.time.max)

    class Meta:
        model = CampaignSchedule
        fields = ('id', 'day', 'start_time', 'end_time')

    def validate(self, attrs):
        attrs['start_time'] = attrs.get('start_time', datetime.time.min)
        attrs['end_time'] = attrs.get('end_time', datetime.time.max)
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
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    start_date = serializers.DateField(allow_null=True)
    targetdevice_set = TargetDeviceSerializer(many=True)
    campaignschedule_set = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['status']

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action

        if action in ['update', 'partial_update']:
            kwargs = extra_kwargs.get('medium', {})
            kwargs['read_only'] = True
            extra_kwargs['medium'] = kwargs

        return extra_kwargs

    def validate_campaignschedule_set(self, value):
        for idx, schedule in enumerate(value):
            start_time = schedule.get('start_time')
            end_time = schedule.get('end_time')
            for i in value[idx + 1:]:
                if schedule['day'] == i['day']:
                    if not (
                            (start_time < i.get('start_time') and end_time < i.get('start_time')) or
                            (start_time > i.get('end_time') and end_time > i.get('end_time'))
                    ):
                        raise serializers.ValidationError(
                            {'campaignschedule_set': 'invalid schedule set.'})

        return value

    def validate(self, attrs):

        if self.instance:
            action = self.context['view'].action
            if action == 'enable':
                attrs = {
                    'is_enable': attrs.get('is_enable', self.instance.is_enable)
                }
                return attrs

            if self.instance.status == Campaign.STATUS_APPROVED:
                raise serializers.ValidationError({"non_field_errors": ["approved campaigns are not editable."]})
            medium = self.instance.medium
            publishers = attrs.get('publishers', self.instance.publishers.all())
            categories = attrs.get('categories', self.instance.categories.all())
        else:
            medium = attrs.get('medium')
            publishers = attrs.get('publishers', [])
            categories = attrs.get('categories', [])

        if len(publishers) == 0 and len(categories) == 0:
            raise serializers.ValidationError("publishers and categories both can not be empty.")

        for category in categories:
            if category.medium != medium:
                raise serializers.ValidationError("campaign's medium and category's medium must be the same.")

        for publisher in publishers:
            if publisher.medium != medium:
                raise serializers.ValidationError("campaign's medium and publisher's medium must be the same.")

        return attrs

    def create(self, validated_data):
        targetdevice_set = validated_data.pop("targetdevice_set")
        schedule_set = validated_data.pop("campaignschedule_set")

        if validated_data['start_date'] is None:
            validated_data["start_date"] = datetime.date.today()

        campaign = super().create(validated_data)

        for targetdevice_data in targetdevice_set:
            TargetDevice.objects.create(campaign=campaign, **targetdevice_data)

        for schedule_data in schedule_set:
            CampaignSchedule.objects.create(campaign=campaign, **schedule_data)

        return campaign

    def update(self, instance, validated_data):
        action = self.context['view'].action
        if action == 'enable':
            instance.is_enable = validated_data.get('is_enable', instance.is_enable)
            instance.save()
            return instance

        targetdevice_set = validated_data.pop("targetdevice_set", None)
        schedule_set = validated_data.pop("campaignschedule_set", None)

        instance = super().update(instance, validated_data)

        if targetdevice_set is not None:
            targetdevice_id_list = [i.get("id") for i in targetdevice_set if i.get("id")]
            TargetDevice.objects.filter(campaign=instance).exclude(id__in=targetdevice_id_list).delete()

            for targetdevice_data in targetdevice_set:
                targetdevice_id = targetdevice_data.pop('id', None)
                if targetdevice_id:
                    TargetDevice.objects.filter(
                        id=targetdevice_id, campaign=instance
                    ).update(**targetdevice_data)
                else:
                    TargetDevice.objects.create(campaign=instance, **targetdevice_data)

        if schedule_set is not None:
            schedule_id_list = [i.get("id") for i in schedule_set if i.get("id")]
            CampaignSchedule.objects.filter(campaign=instance).exclude(id__in=schedule_id_list).delete()
            for schedule_data in schedule_set:
                schedule_id = schedule_data.pop('id', None)
                if schedule_id:
                    CampaignSchedule.objects.filter(
                        id=schedule_id, campaign=instance
                    ).update(**schedule_data)
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
