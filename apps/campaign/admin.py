from django.contrib import admin

from .forms import ContentAdminForm, CampaignAdminForm
from .models import (
    Province,
    Campaign,
    CampaignContent,
    TargetDevice,
    CampaignSchedule,
    CampaignReference,
    TelegramCampaign,
)
from .views import test_campaign


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
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignAdminForm
    list_display = ['name', 'owner', 'medium', 'status', 'is_enable']
    change_form_template = 'campaign/change_form.html'
    inlines = [CampaignContentInline, TargetDeviceInline]
    autocomplete_fields = ["owner"]
    search_fields = ['medium', 'owner__username', 'name', 'contents__title']
    list_filter = ['medium', 'status', 'is_enable']
    filter_horizontal = ['categories', 'locations', 'publishers', 'final_publishers']
    radio_fields = {'status': admin.VERTICAL}
    readonly_fields = ('name', 'owner', 'locations', 'description',
                       'start_date', 'end_date', 'publishers', 'categories',
                       'utm_campaign', 'utm_content', 'medium', 'utm_medium')

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
class CampaignContentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "title", "data")
    list_filter = ("campaign__name", "campaign__categories")
    search_fields = ("campaign__name", "title",)
    form = ContentAdminForm


@admin.register(CampaignSchedule)
class CampaignScheduleAdmin(admin.ModelAdmin):
    list_display = ("campaign", "week_day", "start_time", "end_time")
    search_fields = ("campaign__name",)


@admin.register(CampaignReference)
class CampaignReferenceAdmin(admin.ModelAdmin):
    list_display = ("campaign", "ref_id", "date", "schedule_range")
    search_fields = ('campaign__name', 'ref_id')
    list_filter = ('date', 'campaign__medium')


@admin.register(TelegramCampaign)
class TelegramCampaignAdmin(admin.ModelAdmin):
    list_display = ("campaign", "screenshot")
    search_fields = ("campaign__name",)
