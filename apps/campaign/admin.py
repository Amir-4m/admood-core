from django.contrib import admin, messages

from apps.accounts.admin_filter import OwnerFilter
from services.utils import AutoFilter
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


# --- Inlines ---
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
    readonly_fields = ('week_day', 'start_time', 'end_time')
    can_delete = False
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
    list_display = ['name', 'owner', 'medium', 'status', 'is_enable']
    change_form_template = 'campaign/change_form.html'
    inlines = [CampaignContentInline, CampaignScheduleInline, TargetDeviceInline, FinalPublisherInline]
    autocomplete_fields = ["owner"]
    actions = ['make_approve_campaigns']
    search_fields = ['medium', 'name', 'contents__title']
    list_filter = [OwnerFilter, 'medium', 'status', 'is_enable']
    filter_horizontal = ['categories', 'locations', 'publishers', 'final_publishers']
    radio_fields = {'status': admin.VERTICAL}
    readonly_fields = (
        'owner', 'locations', 'description', 'start_date', 'end_date', 'publishers', 'categories', 'utm_campaign',
        'utm_content', 'medium', 'utm_medium', 'error_count', 'is_enable'
    )

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


@admin.register(CampaignContent)
class CampaignContentAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ("campaign", "title", "data")
    readonly_fields = ['data']
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
    list_display = ("campaign", "ref_id", "date", "schedule_range")
    readonly_fields = ['extra_data']
    raw_id_fields = ['campaign']
    search_fields = ('ref_id',)
    list_filter = (CampaignFilter, 'date', 'campaign__medium')


@admin.register(TelegramCampaign)
class TelegramCampaignAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ("campaign", "screenshot")
    raw_id_fields = ('screenshot', 'campaign')
    list_filter = [CampaignFilter]
