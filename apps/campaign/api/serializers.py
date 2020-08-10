import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.campaign.models import Province, Campaign, CampaignContent, CampaignSchedule, TargetDevice
from apps.core.models import File
from apps.medium.consts import Medium


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
    target_devices = TargetDeviceSerializer(allow_null=True, many=True)
    schedules = CampaignScheduleSerializer(many=True)

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

    def validate_schedules(self, value):
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
                            {'schedules': 'invalid schedule set.'})

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
        target_devices = validated_data.pop("target_devices")
        schedules = validated_data.pop("schedules")

        if validated_data['start_date'] is None:
            validated_data["start_date"] = datetime.date.today()

        campaign = super().create(validated_data)

        for target_device_data in target_devices:
            TargetDevice.objects.create(campaign=campaign, **target_device_data)

        for schedule_data in schedules:
            CampaignSchedule.objects.create(campaign=campaign, **schedule_data)

        return campaign

    def update(self, instance, validated_data):
        action = self.context['view'].action
        if action == 'enable':
            instance.is_enable = validated_data.get('is_enable', instance.is_enable)
            instance.save()
            return instance

        target_devices = validated_data.pop("target_devices", None)
        schedules = validated_data.pop("schedules", None)

        instance = super().update(instance, validated_data)

        if target_devices is not None:
            target_device_id_list = [i.get("id") for i in target_devices if i.get("id")]
            TargetDevice.objects.filter(campaign=instance).exclude(id__in=target_device_id_list).delete()

            for target_device_data in target_devices:
                target_device_id = target_device_data.pop('id', None)
                if target_device_id:
                    TargetDevice.objects.filter(
                        id=target_device_id, campaign=instance
                    ).update(**target_device_data)
                else:
                    TargetDevice.objects.create(campaign=instance, **target_device_data)

        if schedules is not None:
            schedule_id_list = [i.get("id") for i in schedules if i.get("id")]
            CampaignSchedule.objects.filter(campaign=instance).exclude(id__in=schedule_id_list).delete()
            for schedule_data in schedules:
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


class CampaignRepeatSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(allow_null=True)
    target_devices = TargetDeviceSerializer(many=True)
    schedules = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = ["start_date", 'end_date', 'daily_cost', 'total_cost', 'target_devices', 'schedules']


class TelegramContentDataSerializer(serializers.Serializer):
    content = serializers.CharField(required=False)
    links = serializers.ListField(required=False)
    inlines = serializers.ListField(required=False)
    file = serializers.IntegerField(required=False)
    file_type = serializers.CharField(required=False)
    view_type = serializers.CharField(required=False)

    def validate_file(self, value):
        if File.objects.filter(pk=value).exists():
            return value
        else:
            raise ValidationError({'data': 'invalid file id'})

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            file = File.objects.get(pk=data['file']).file
            file_path = file.url
        except:
            file_path = ''
        data.update({'file': file_path})
        return data


class WebContentDataSerializer(serializers.Serializer):
    subtitle = serializers.CharField(required=False)
    imageId = serializers.IntegerField(required=False)
    imgTitle = serializers.CharField(required=False)
    imgDescription = serializers.CharField(required=False)

    def validate_imageId(self, value):
        if File.objects.filter(pk=value).exists():
            return value
        else:
            raise ValidationError({'data': 'invalid imageId'})

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            image = File.objects.get(pk=data['imageId']).file
            image_path = image.url
        except:
            image_path = ''
        data.update({'imageId': image_path})
        return data


class CampaignContentSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = CampaignContent
        fields = '__all__'
        read_only_fields = ['campaign']

    def get_data(self, instance):
        if instance.campaign.medium == Medium.TELEGRAM:
            serializer = TelegramContentDataSerializer
        elif instance.campaign.medium == Medium.WEB:
            serializer = WebContentDataSerializer
        # todo: add other mediums
        else:
            return None
        return serializer(instance.data).data
