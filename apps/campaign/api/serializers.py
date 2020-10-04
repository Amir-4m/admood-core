import datetime

from django.utils import timezone
from rest_framework import serializers

from apps.campaign.models import Province, Campaign, CampaignContent, CampaignSchedule, TargetDevice, CampaignPublisher
from apps.core.models import File
from apps.payment.models import Transaction
from services.telegram import get_contents


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
        fields = ('id', 'week_day', 'start_time', 'end_time')

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
                if schedule['week_day'] == i['week_day']:
                    if not (
                            (start_time < i.get('start_time') and end_time < i.get('start_time')) or
                            (start_time > i.get('end_time') and end_time > i.get('end_time'))
                    ):
                        raise serializers.ValidationError(
                            {'schedules': 'invalid schedule set.'})

        return value

    def validate_start_date(self, value):
        if value is None:
            value = timezone.now().date()
        return value

    def validate_total_cost(self, value):
        user = self.context['request'].user
        if value > Transaction.balance(user):
            raise serializers.ValidationError(
                {'total_cost': 'Ensure this value is less than or equal to your wallet balance.'})
        return value

    def validate(self, attrs):
        action = self.context['view'].action
        if action in ['enable']:
            return attrs

        if self.instance:
            if self.instance.status != Campaign.STATUS_DRAFT:
                raise serializers.ValidationError({"non_field_errors": ["only draft campaigns are editable."]})
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

        campaign = super().create(validated_data)

        for target_device_data in target_devices:
            TargetDevice.objects.create(campaign=campaign, **target_device_data)

        for schedule_data in schedules:
            CampaignSchedule.objects.create(campaign=campaign, **schedule_data)

        for count, publisher in enumerate(campaign.publishers.all()):
            CampaignPublisher.objects.create(
                campaign=campaign,
                publisher=publisher,
                publisher_price=0,
                advertiser_price=0,
                order=count + 1
            )

        return campaign

    def update(self, instance, validated_data):
        target_devices = validated_data.pop("target_devices", None)
        schedules = validated_data.pop("schedules", None)
        publishers = instance.publishers.all()

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

        CampaignPublisher.objects.filter(campaign=instance).delete()
        for count, publisher in enumerate(publishers):
            CampaignPublisher.objects.create(
                campaign=instance,
                publisher=publisher,
                publisher_price=0,
                advertiser_price=0,
                order=count + 1
            )

        return instance


class CampaignEnableSerializer(serializers.ModelSerializer):
    is_enable = serializers.BooleanField(required=True)

    class Meta:
        model = Campaign
        fields = ["is_enable"]


class CampaignApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ('status',)

    def validate(self, attrs):
        if self.instance.status != Campaign.STATUS_DRAFT:
            raise serializers.ValidationError(
                {'status': 'Ensure this campaign is a draft.'})
        if self.instance.total_cost > Transaction.balance(self.instance.owner):
            raise serializers.ValidationError(
                {'total_cost': 'Ensure this value is less than or equal to your wallet balance.'})
        return attrs

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        Transaction.objects.create(user=instance.owner, value=-instance.total_cost)
        return instance


class CampaignRepeatSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(allow_null=True)
    schedules = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = ['start_date', 'end_date', 'daily_cost', 'total_cost', 'schedules', 'categories', 'publishers']

    def validate(self, attrs):
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


class CampaignDuplicateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(allow_null=True)
    schedules = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = ['id', 'schedules', 'name', 'start_date', 'end_date', 'total_cost', 'daily_cost']

    def validate_schedules(self, value):
        for idx, schedule in enumerate(value):
            start_time = schedule.get('start_time')
            end_time = schedule.get('end_time')
            for i in value[idx + 1:]:
                if schedule['week_day'] == i['week_day']:
                    if not (
                            (start_time < i.get('start_time') and end_time < i.get('start_time')) or
                            (start_time > i.get('end_time') and end_time > i.get('end_time'))
                    ):
                        raise serializers.ValidationError(
                            {'schedules': 'invalid schedule set.'})

        return value

    def validate_start_date(self, value):
        if value is None:
            value = timezone.now().date()
        return value

    def validate(self, attrs):
        if self.instance.status not in [Campaign.STATUS_APPROVED, Campaign.STATUS_DRAFT]:
            raise serializers.ValidationError({
                "non_field_errors": ["draft and approved campaigns are just duplicable."]})
        return attrs

    def update(self, instance, validated_data):
        contents = instance.contents.all()
        locations = instance.locations.all()
        target_devices = instance.target_devices.all()
        schedules = validated_data.pop("schedules", None)
        campaign_publishers = instance.campaignpublisher_set.all()

        if instance.status == Campaign.STATUS_APPROVED:
            telegram_contents = get_contents(instance.campaignreference_set.first().reference_id)
            for count, tc in enumerate(telegram_contents):
                for file in tc.get("files", []):
                    telegram_file_hash = file["telegram_file_hash"]
                    telegram_content = instance.contents.all()[count]
                    telegram_content.data["telegram_file_hash"] = telegram_file_hash
                    telegram_content.save()

        instance.pk = None
        super().update(instance, validated_data)

        instance.locations.set(locations)

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

        for content in contents:
            content.pk = None
            content.campaign = instance
            content.save()

        for target_device in target_devices:
            target_device.pk = None
            target_device.campaign = instance
            target_device.save()

        for campaign_publisher in campaign_publishers:
            campaign_publisher.pk = None
            campaign_publisher.campaign = instance
            campaign_publisher.save()

        return instance


class CampaignContentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    campaign_status = serializers.ReadOnlyField()
    campaign_medium = serializers.ReadOnlyField()

    class Meta:
        model = CampaignContent
        fields = '__all__'
        read_only_fields = ['campaign']

    def validate(self, attrs):
        if self.instance and self.instance.campaign.status == Campaign.STATUS_APPROVED:
            raise serializers.ValidationError({"non_field_errors": ["approved campaigns are not editable."]})
        return attrs

    def get_file_url(self, obj):
        try:
            file_id = obj.data.get('file') or obj.data.get('imageId')
            file = File.objects.get(pk=file_id).file
            return self.context['request'].build_absolute_uri(file.url)
        except:
            return None
