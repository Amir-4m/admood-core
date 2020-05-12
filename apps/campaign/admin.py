from django.contrib import admin
from .models import (
    Province,
    Campaign,
    CampaignContent,
    TargetDevice,
    CampaignSchedule,
)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class TargetDeviceInline(admin.TabularInline):
    model = TargetDevice
    extra = 1


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    inlines = [TargetDeviceInline]
    autocomplete_fields = ["owner", "publishers", "locations"]


@admin.register(CampaignContent)
class CampaignContentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "title", "data")


@admin.register(CampaignSchedule)
class CampaignScheduleAdmin(admin.ModelAdmin):
    list_display = ("campaign", "day", "start_time", "end_time")
