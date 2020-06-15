from django.contrib import admin
from .models import (
    Device,
    Platform,
    OS,
    Version,
)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "parent")
    fields = ("parent", "title")


class PlatformAdmin(DeviceAdmin):
    fields = ("title",)


class OSAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Device.objects.filter(type=Device.TYPE_PLATFORM)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class VersionAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Device.objects.filter(type=Device.TYPE_OS)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# admin.site.register(Device, DeviceAdmin)
admin.site.register(Platform, PlatformAdmin)
admin.site.register(OS, OSAdmin)
admin.site.register(Version, VersionAdmin)
