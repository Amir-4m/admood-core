from django.contrib import admin
from .models import (
    Province,
    Campaign,
    CampaignContent,
    TargetDevice,
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
    autocomplete_fields = ["owner", "publisher", "locations"]


@admin.register(CampaignContent)
class CampaignContentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "title", "data")

