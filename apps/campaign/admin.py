from django.contrib import admin
from .models import (
    Province,
    Campaign,
    Content,
    TargetDevice,
)


class TargetDeviceInline(admin.TabularInline):
    model = TargetDevice
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
    inlines = [TargetDeviceInline]


class ContentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "title", "subtitle", "data")


admin.site.register(Province)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(TargetDevice)
