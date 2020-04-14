from django.contrib import admin
from .models import (
    Province,
    Campaign,
    CampaignContent,
    TargetDevice,
)


class TargetDeviceInline(admin.TabularInline):
    model = TargetDevice
    extra = 1


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    inlines = [TargetDeviceInline]


@admin.register(CampaignContent)
class CampaignContentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "title", "subtitle", "data")


admin.site.register(Province)
