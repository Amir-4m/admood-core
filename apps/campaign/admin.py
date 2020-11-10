from django.contrib import admin

from .forms import ContentAdminForm
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
    extra = 0


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'medium', 'status', 'is_enable']
    change_form_template = 'campaign/change_form.html'
    inlines = [CampaignContentInline, TargetDeviceInline]
    autocomplete_fields = ["owner"]
    search_fields = ['medium', 'owner__username']
    list_filter = ['medium', 'status', 'is_enable']
    filter_horizontal = ['categories', 'locations', 'publishers']

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
    search_fields = ("campaign__name", "title",)
    form = ContentAdminForm


@admin.register(CampaignSchedule)
class CampaignScheduleAdmin(admin.ModelAdmin):
    list_display = ("campaign", "week_day", "start_time", "end_time")
    search_fields = ("campaign__name",)


@admin.register(CampaignReference)
class CampaignReferenceAdmin(admin.ModelAdmin):
    list_display = ("campaign", "ref_id", "date", "start_time", "end_time")
    search_fields = ('campaign__name', 'ref_id')
    list_filter = ('date', 'start_time', 'end_time')


@admin.register(TelegramCampaign)
class TelegramCampaignAdmin(admin.ModelAdmin):
    list_display = ("campaign", "screenshot")
    search_fields = ("campaign__name",)
