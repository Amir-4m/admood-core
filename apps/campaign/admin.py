from django.contrib import admin
from .models import (
    Province,
    Campaign,
    TargetDevice,
    Content,
)


class TargetDeviceAdmin(admin.ModelAdmin):
    list_display = ("campaign", "platform", "os", "os_version", "service_provider")


class ContentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "title", "subtitle", "data")


admin.site.register(Province)
admin.site.register(Campaign)
admin.site.register(TargetDevice, TargetDeviceAdmin)
admin.site.register(Content, ContentAdmin)
