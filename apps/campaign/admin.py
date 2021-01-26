from django.contrib import admin

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


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ["name"]


class TargetDeviceInline(admin.TabularInline):
    model = TargetDevice
    extra = 1


class CampaignContentInline(admin.TabularInline):
    model = CampaignContent
    show_change_link = True
    fields = ('title', 'cost_model_price', 'cost_model', 'is_hidden')
    readonly_fields = ('title', 'cost_model_price', 'cost_model', 'is_hidden')
    can_delete = False


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin, AutoFilter):
    form = CampaignAdminForm
    list_display = ['name', 'owner', 'medium', 'status', 'is_enable']
    change_form_template = 'campaign/change_form.html'
    inlines = [CampaignContentInline, TargetDeviceInline, FinalPublisherInline]
    autocomplete_fields = ["owner"]
    search_fields = ['medium', 'name', 'contents__title']
    list_filter = [OwnerFilter, 'medium', 'status', 'is_enable']
    filter_horizontal = ['categories', 'locations', 'publishers', 'final_publishers']
    radio_fields = {'status': admin.VERTICAL}

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = (
            'owner', 'locations', 'description', 'start_date', 'end_date', 'publishers', 'categories', 'utm_campaign',
            'utm_content', 'medium', 'utm_medium'
        )
        if obj and obj.status == Campaign.STATUS_DRAFT:  # name field editable
            return readonly_fields
        return readonly_fields + ('name',)

    def render_change_form(self, request, context, **kwargs):
        return super().render_change_form(request, context, **kwargs)

    def get_urls(self):
        from django.urls import path
        url_patterns = [
            path(r'<int:pk>/test/', test_campaign, name="test_campaign"),
        ]
        url_patterns += super().get_urls()
        return url_patterns


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
    list_display = ("campaign", "ref_id", "date", "schedule_range")
    raw_id_fields = ['campaign']
    search_fields = ('ref_id',)
    list_filter = (CampaignFilter, 'date', 'campaign__medium')


@admin.register(TelegramCampaign)
class TelegramCampaignAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ("campaign", "screenshot")
    list_filter = [CampaignFilter]
