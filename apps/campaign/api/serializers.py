import logging
import datetime
from datetime import timedelta

from django.db.models.functions import Lower
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from khayyam import JalaliDatetime
from rest_framework import serializers

from apps.campaign.models import Province, Campaign, CampaignContent, CampaignSchedule, TargetDevice, CampaignReference
from apps.campaign.utils import get_hourly_report_dashboard, compute_telegram_cost
from apps.core.consts import CostModel
from apps.core.models import File
from apps.medium.consts import Medium
from apps.medium.models import Publisher, Category
from apps.medium.api.serializers import CategorySerializer, MinorPublisherSerializer
from apps.payments.models import Transaction
from services.utils import file_type

logger = logging.getLogger(__file__)


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
                {'end_time': _('end_time should be greater than start_time')},
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
    campaign_references = serializers.SerializerMethodField()
    utm_campaign_default = serializers.SerializerMethodField()
    utm_medium_default = serializers.SerializerMethodField()
    utm_content_default = serializers.SerializerMethodField()
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    final_publishers = MinorPublisherSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['status']

    def to_representation(self, instance):
        data = super(CampaignSerializer, self).to_representation(instance)
        data['categories'] = CategorySerializer(Category.objects.filter(id__in=data['categories']),many=True).data

        data['publishers'] = MinorPublisherSerializer(
            Publisher.objects.filter(id__in=data['publishers']),
            many=True
        ).data
        data['locations'] = ProvinceSerializer(Province.objects.filter(id__in=data['locations']), many=True).data

        return data

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action

        if action in ['update', 'partial_update']:
            kwargs = extra_kwargs.get('medium', {})
            kwargs['read_only'] = True
            extra_kwargs['medium'] = kwargs

        return extra_kwargs

    def get_campaign_references(self, obj):
        return obj.campaignreference_set.annotate(
            display_text=Lower('schedule_range')
        ).values('id', 'display_text')

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
                            {'schedules': _('invalid schedule set.')})

        return value

    def validate_start_date(self, value):
        if value is None:
            value = timezone.now().date()
        return value

    def validate_total_budget(self, value):
        user = self.context['request'].user
        if value > Transaction.balance(user):
            raise serializers.ValidationError(
                {'total_budget': _('Ensure total budget is less than or equal to your wallet balance.')})
        return value

    def validate(self, attrs):
        if self.instance:
            if self.instance.status != Campaign.STATUS_DRAFT:
                raise serializers.ValidationError({"non_field_errors": [_("only draft campaigns are editable.")]})
            medium = self.instance.medium
            publishers = attrs.get('publishers', self.instance.publishers.all())
            categories = attrs.get('categories', self.instance.categories.all())
        else:
            medium = attrs.get('medium')
            publishers = attrs.get('publishers', [])
            categories = attrs.get('categories', [])

        if len(publishers) == 0 and len(categories) == 0:
            raise serializers.ValidationError(_("publishers and categories both can not be empty."))

        for category in categories:
            if category.medium != medium:
                raise serializers.ValidationError(_("campaign's medium and category's medium must be the same."))

        for publisher in publishers:
            if publisher.medium != medium:
                raise serializers.ValidationError(_("campaign's medium and publisher's medium must be the same."))

        return attrs

    def create(self, validated_data):
        target_devices = validated_data.pop("target_devices")
        schedules = validated_data.pop("schedules")

        campaign = super().create(validated_data)

        for target_device_data in target_devices:
            TargetDevice.objects.create(campaign=campaign, **target_device_data)

        for schedule_data in schedules:
            CampaignSchedule.objects.create(campaign=campaign, **schedule_data)

        return campaign

    def update(self, instance, validated_data):
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

    def get_utm_campaign_default(self, obj):
        return obj.id

    def get_utm_medium_default(self, obj):
        return obj.get_medium_display()

    def get_utm_content_default(self, obj):
        return 'کانال نمایش دهنده تبلیغ'


class CampaignEnableSerializer(serializers.ModelSerializer):
    is_enable = serializers.BooleanField(required=True)

    class Meta:
        model = Campaign
        fields = ["is_enable"]

    def validate(self, attrs):
        if self.instance.is_finished():
            raise serializers.ValidationError(
                {"is_enable": _("campaign total budget is low or time has been expired.")}
            )
        return attrs


class CampaignRepeatSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(allow_null=True)
    schedules = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = ['start_date', 'end_date', 'daily_budget', 'total_budget', 'schedules', 'categories', 'publishers']

    def validate(self, attrs):
        medium = attrs.get('medium')
        publishers = attrs.get('publishers', [])
        categories = attrs.get('categories', [])
        if len(publishers) == 0 and len(categories) == 0:
            raise serializers.ValidationError(_("publishers and categories both can not be empty."))

        for category in categories:
            if category.medium != medium:
                raise serializers.ValidationError(_("campaign's medium and category's medium must be the same."))

        for publisher in publishers:
            if publisher.medium != medium:
                raise serializers.ValidationError(_("campaign's medium and publisher's medium must be the same."))


class CampaignDuplicateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(allow_null=True)
    schedules = CampaignScheduleSerializer(many=True)

    class Meta:
        model = Campaign
        fields = ['id', 'schedules', 'name', 'start_date', 'end_date', 'total_budget', 'daily_budget']

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
                            {'schedules': _('invalid schedule set.')})

        return value

    def validate_start_date(self, value):
        if value is None:
            value = timezone.now().date()
        return value

    def validate(self, attrs):
        if self.instance.status not in [Campaign.STATUS_APPROVED, Campaign.STATUS_DRAFT]:
            raise serializers.ValidationError({
                "non_field_errors": [_("draft and approved campaigns are just duplicable.")]})
        return attrs

    def update(self, instance, validated_data):
        locations = instance.locations.all()
        publishers = instance.publishers.all()
        categories = instance.categories.all()
        contents = instance.contents.all()
        target_devices = instance.target_devices.all()
        schedules = validated_data.pop("schedules", None)

        instance.pk = None
        super().update(instance, validated_data)

        instance.locations.set(locations)
        instance.publishers.set(publishers)
        instance.categories.set(categories)

        for schedule_data in schedules:
            CampaignSchedule.objects.create(
                campaign=instance,
                week_day=schedule_data['week_day'],
                start_time=schedule_data['start_time'],
                end_time=schedule_data['end_time'],
            )

        for content in contents:
            content.pk = None
            content.campaign = instance
            content.save()

        for target_device in target_devices:
            target_device.pk = None
            target_device.campaign = instance
            target_device.save()

        return instance


class CampaignContentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    campaign_status = serializers.ReadOnlyField()
    campaign_medium = serializers.ReadOnlyField()

    class Meta:
        model = CampaignContent
        exclude = ('is_hidden',)
        read_only_fields = ('campaign',)

    def validate(self, attrs):
        data = attrs.get('data')
        is_igtv = data.get('is_igtv')
        files = data.get('file')

        try:
            campaign = Campaign.objects.get(id=self.context['view'].kwargs['campaign_id'])
            attrs.update({'campaign': campaign})

        except Campaign.DoesNotExist:
            raise serializers.ValidationError({"campaign": _("campaign with this id does not exist!")})

        if self.instance and self.instance.campaign.status == Campaign.STATUS_APPROVED:
            raise serializers.ValidationError({"non_field_errors": [_("approved campaigns are not editable.")]})

        # validating instagram medium type campaign contents
        if campaign.medium in [Medium.INSTAGRAM_STORY, Medium.INSTAGRAM_POST]:
            if not self.instance and campaign.contents.all().count() > 0:
                raise serializers.ValidationError({"content": _("instagram campaigns can only have 1 content!")})

            if attrs['cost_model'] not in [CostModel.CPR, CostModel.CPI]:
                raise serializers.ValidationError({"cost_model": [_("invalid value for cost model")]})

            if is_igtv and files is not None:
                file = File.objects.filter(pk=files[0]).first()

                if file is not None and file_type(file.__str__()) != 'video':
                    raise serializers.ValidationError({"file": _("file format is not valid!")})

                if len(files) > 1:
                    raise serializers.ValidationError({"file": _("igtv can only have 1 file!")})

            elif not is_igtv and files:
                if len(files) > 10:
                    raise serializers.ValidationError({"campaign": _("album posts can not have more 10 files!")})
        return attrs

    def get_file_url(self, obj):
        try:
            files = obj.data.get('file')
            if files is not None and isinstance(files, list):
                file_urls = []
                for f_id in files:
                    try:
                        file_obj = File.objects.get(pk=f_id)
                    except File.DoesNotExist:
                        continue
                    file_urls.append({
                        "id": file_obj.id,
                        "file": self.context['request'].build_absolute_uri(file_obj.file.url),
                        "type": file_type(file_obj.__str__())
                    })
                return file_urls
            else:
                file_id = files or obj.data.get('imageId')
                file = File.objects.get(pk=file_id).file
                return self.context['request'].build_absolute_uri(file.url)
        except Exception as e:
            logger.error(f'[getting file url for campaign content failed]-[campaing content id: {obj.id}]-[exc: {e}]')
            return None


class CampaignReferenceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='campaign.name')
    contents_detail = serializers.SerializerMethodField()
    publishers_detail = serializers.SerializerMethodField()
    display_text = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = CampaignReference
        fields = ('id', 'title', 'date', 'display_text', 'contents_detail', 'publishers_detail')

    def contents_detail_handler(self, obj):
        campaign_contents = CampaignContent.objects.filter(
            id__in=[item['content'] for item in obj.contents],
            cost_model_price__gt=0
        ).values('id', 'title')
        result = []
        for content in obj.contents:
            for cc in campaign_contents:
                if cc['id'] == content['content']:
                    result.append({
                        'content_title': cc['title'],
                        'content_total_views': content['views'],
                        'hourly_graph_cumulative': content.get('graph_hourly_cumulative'),
                        'hourly_graph_view': content.get('graph_hourly_view')
                    })
        return result

    def get_contents_detail(self, obj):
        contents_detail = []
        if self.context['view'].action != 'report':
            return contents_detail
        if obj.campaign.medium == Medium.TELEGRAM:
            contents_detail = self.contents_detail_handler(obj)

        return contents_detail

    def get_date(self, obj):
        return f"{obj.schedule_range.lower.date()}"

    def get_display_text(self, obj):
        if obj.schedule_range:
            return f"{obj.schedule_range.lower.time()} - {obj.schedule_range.lower.date()}"
        return f"{obj.campaign.name} - {obj.id}"

    def get_publishers_detail(self, obj):
        if self.context['view'].action != 'report':
            return []
        publishers_detail = []
        if obj.campaign.medium == Medium.TELEGRAM:
            for content in obj.contents:
                for detail in content.get('detail', []):
                    publishers_detail.append(dict(
                        publishers=Publisher.objects.filter(ref_id__in=detail.get('channel_ids', [])).values(
                            'name', 'extra_data__tag'
                        ),
                        posts=detail.get('posts', []))
                    )
        return publishers_detail


class EstimateActionsSerializer(serializers.Serializer):
    publishers = serializers.ListField(child=serializers.IntegerField())
    categories = serializers.ListField(child=serializers.IntegerField())
    budget = serializers.IntegerField()


class CampaignDashboardReportSerializer(serializers.Serializer):
    CHART_LINE = 'line'
    CHART_COLUMN = 'column'
    CHART_AREA = 'area'
    DAILY = 'daily'
    HOURLY = 'hourly'

    medium = serializers.ChoiceField(choices=Medium.MEDIUM_CHOICES, required=True, write_only=True)

    start_date = serializers.DateField(required=False, write_only=True)
    end_date = serializers.DateField(required=False, write_only=True)
    last_days = serializers.IntegerField(required=False, write_only=True)

    active_campaigns = serializers.SerializerMethodField()
    report = serializers.SerializerMethodField()

    def handle_filter_data(self):
        start_date = self.validated_data.get('start_date')
        end_date = self.validated_data.get('end_date') or timezone.now().date()
        last_days = self.validated_data.get('last_days') or 0

        if start_date:
            return dict(
                created_time__date__gte=start_date,
                created_time__date__lte=end_date
            )
        return dict(created_time__date__gte=timezone.now() - timedelta(days=last_days))

    def handle_display_type(self):
        last_days = self.validated_data.get('last_days')

        if last_days == 0:
            return self.HOURLY
        else:
            return self.DAILY

    @property
    def campaigns(self):
        filter_kwargs = dict(
            status=Campaign.STATUS_APPROVED,
            medium=self.validated_data.get('medium')
        )
        filter_kwargs.update(self.handle_filter_data())

        if 'owner_id' in self.context.keys():
            filter_kwargs.update(dict(owner_id=self.context.get('owner_id')))

        return Campaign.objects.filter(**filter_kwargs)

    def get_active_campaigns(self, obj):
        return self.campaigns.count()

    def get_report(self, obj):
        total_view = 0
        total_cost = 0
        temp_reports = []
        view_chart_type, cost_chart_type = self.CHART_LINE, self.CHART_AREA
        campaign_ids = self.campaigns.values_list('id', flat=True)

        filter_kwargs = dict(campaign_id__in=campaign_ids, ref_id__isnull=False)
        filter_kwargs.update(self.handle_filter_data())
        campaign_references = CampaignReference.objects.filter(
            **filter_kwargs
        ).order_by('created_time')

        campaign_contents = CampaignContent.objects.filter(
            campaign_id__in=campaign_ids,
            cost_model_price__gt=0
        )

        for cr in campaign_references:
            for cr_content in cr.contents:
                for cc in campaign_contents:
                    if cr_content.get('content') == cc.id:
                        # total cost
                        total_cost += compute_telegram_cost(
                            views=cr_content.get('views', 0),
                            cost_model_price=cc.cost_model_price
                        )
                        # total view
                        total_view += cr_content.get('views', 0)

                        # collecting all reports for each campaign
                        reports = cr_content.get('graph_hourly_cumulative', [])
                        for rep in reports:
                            rep.update({
                                'y-cost': compute_telegram_cost(views=rep['y'], cost_model_price=cc.cost_model_price),
                                'cr-date': JalaliDatetime(cr.schedule_range.lower).strftime('%y-%m-%d')
                            })
                            temp_reports.append(rep)

        if self.handle_display_type() == self.HOURLY:
            cost_chart, view_chart = get_hourly_report_dashboard(temp_reports, 'name')
        else:
            cost_chart, view_chart = get_hourly_report_dashboard(temp_reports, 'cr-date')  # data of charts
            cost_chart_type, view_chart_type = self.CHART_COLUMN, self.CHART_COLUMN  # type of charts

        return dict(
            total_view=total_view,
            total_cost=total_cost,
            total_view_chart=dict(type=view_chart_type, data=view_chart),
            total_cost_chart=dict(type=cost_chart_type, data=cost_chart),
        )
