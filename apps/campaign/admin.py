from django.utils.translation import ugettext_lazy as _
from django.contrib import admin, messages
from django.contrib.postgres.fields import JSONField
from django.db.models import Q, Count
from django.utils import timezone

from django_json_widget.widgets import JSONEditorWidget

from apps.accounts.admin_filter import OwnerFilter

from services.utils import AutoFilter
from .tasks import update_telegram_reports_from_admin
from .forms import ContentAdminForm, CampaignAdminForm
from .admin_filter import CampaignFilter

from .models import (
    Province,
    Campaign,
    FinalPublisher,
    CampaignContent,
    TargetDevice,
    CampaignSchedule,
    CampaignReference,
    TelegramCampaign,
)
from .views import test_campaign
from apps.core.consts import CostModel

# --- Custom Filter ---
class IsLiveCampaignReferenceFilter(admin.SimpleListFilter):
    title = _('is live')
    parameter_name = 'is_live'

    def lookups(self, request, model_admin):
        return (1, _('yes')), (0, _('no'))

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(**CampaignReference.objects.live_conditions)
        return queryset


# --- Inlines ---
class FinalPublisherInline(admin.TabularInline):
    model = FinalPublisher
    fields = ('publisher', 'get_publisher_main_price', 'tariff')
    readonly_fields = ('publisher', 'get_publisher_main_price')
    extra = 0

    def get_publisher_main_price(self, obj):
        return obj.publisher.cost_models.filter(
            cost_model=CostModel.CPV
        ).order_by('-publisher_price').first().publisher_price
    get_publisher_main_price.short_description = 'publisher main price'


class TargetDeviceInline(admin.TabularInline):
    model = TargetDevice
    extra = 1


class CampaignContentInline(admin.TabularInline):
    model = CampaignContent
    show_change_link = True
    fields = ('title', 'cost_model_price', 'cost_model', 'is_hidden')
    readonly_fields = ('title', 'cost_model_price', 'cost_model', 'is_hidden')
    can_delete = False
    extra = 0


class CampaignScheduleInline(admin.TabularInline):
    model = CampaignSchedule
    fields = ('week_day', 'start_time', 'end_time')
    show_change_link = True
    extra = 0


# --- Model Admins ---
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ["name"]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin, AutoFilter):
    form = CampaignAdminForm
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_display = ['name', 'owner', 'medium', 'status', 'is_enable']
    change_form_template = 'campaign/change_form.html'
    inlines = [CampaignContentInline, CampaignScheduleInline, TargetDeviceInline, FinalPublisherInline]
    autocomplete_fields = ["owner"]
    actions = ['make_approve_campaigns', 'update_views_from_adtel']
    search_fields = ['medium', 'name', 'contents__title']
    list_filter = [OwnerFilter, 'medium', 'status', 'is_enable', 'created_time']
    filter_horizontal = ['categories', 'locations', 'publishers', 'final_publishers']
    radio_fields = {'status': admin.VERTICAL}
    readonly_fields = (
        'owner', 'is_enable', 'locations', 'description', 'start_date', 'end_date', 'publishers', 'categories',
        'utm_campaign', 'utm_content', 'medium', 'utm_medium', 'error_count', 'total_cost', 'remaining_views',
        'today_cost'
    )

    def has_add_permission(self, request):
        """Creating new campaign from admin panel is disabled."""
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not CampaignReference.objects.filter(
                campaign=obj,
                ref_id__isnull=False
        ).exists():
            return readonly_fields
        return ('name',) + readonly_fields

    def render_change_form(self, request, context, **kwargs):
        return super().render_change_form(request, context, **kwargs)

    def get_urls(self):
        from django.urls import path
        url_patterns = [
            path(r'<int:pk>/test/', test_campaign, name="test_campaign"),
        ]
        url_patterns += super().get_urls()
        return url_patterns

    def make_approve_campaigns(self, request, queryset):
        valid_objs = []
        for q in queryset.filter(status=Campaign.STATUS_WAITING):
            valid, msg_err = q.approve_validate(status=Campaign.STATUS_APPROVED)
            if valid:
                q.status = Campaign.STATUS_APPROVED
                valid_objs.append(q)
            else:
                messages.error(request, f"{msg_err}, campaign id: {q.id} - name: {q.name}")
        Campaign.objects.bulk_update(valid_objs, fields=['status'])
        messages.info(request, f'{len(valid_objs)} Campaign updated!')

    def update_views_from_adtel(self, request, queryset):
        update_telegram_reports_from_admin.apply_async(
            args=tuple(CampaignReference.objects.filter(campaign__in=queryset).values_list('id', flat=True))
        )


@admin.register(CampaignContent)
class CampaignContentAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ("campaign", "title", "data")
    list_filter = (CampaignFilter, "campaign__categories")
    raw_id_fields = ['campaign']
    search_fields = ("title",)
    ordering = ['-id']
    form = ContentAdminForm


@admin.register(CampaignSchedule)
class CampaignScheduleAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ("campaign", "week_day", "start_time", "end_time")
    raw_id_fields = ['campaign']
    list_filter = [CampaignFilter]


@admin.register(CampaignReference)
class CampaignReferenceAdmin(admin.ModelAdmin, AutoFilter):
    list_display = (
        "campaign", "ref_id", "schedule_range_start", "schedule_range_end", "views", "ref_ids", 'created_time',
        'is_live'
    )
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    readonly_fields = ['extra_data', 'created_time', 'updated_time']
    raw_id_fields = ['campaign']
    search_fields = ('ref_id',)
    list_filter = (CampaignFilter, 'campaign__medium', IsLiveCampaignReferenceFilter)  # 'is_live'

    def iterate_contents(self, contents, key):
        result = []
        if len(contents) != 0:
            for content in contents:
                result.append(content.get(key, '_'))
        return result

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            # live condition
            _is_live=Count(
                'id',
                filter=Q(**CampaignReference.objects.live_conditions)
            )
        )
        return queryset

    # custom fields
    def is_live(self, obj):
        return obj._is_live
    is_live.admin_order_field = '_is_live'
    is_live.boolean = True

    def schedule_range_start(self, obj):
        return getattr(obj.schedule_range, 'lower', '')

    def schedule_range_end(self, obj):
        return getattr(obj.schedule_range, 'upper', '')

    def views(self, obj):
        all_views = self.iterate_contents(obj.contents, 'views')
        return str(all_views) if all_views else ""

    def ref_ids(self, obj):
        all_message_id = self.iterate_contents(obj.contents, 'ref_id')
        return str(all_message_id).replace('\'', '') if all_message_id else ""


@admin.register(TelegramCampaign)
class TelegramCampaignAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ("campaign", "screenshot")
    raw_id_fields = ('screenshot', 'campaign')
    list_filter = [CampaignFilter]
