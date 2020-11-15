from django.contrib import admin
from .models import (
    Device,
    Platform,
    OS,
    Version,
)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ("title", "parent")
    fields = ("parent", "title")
    search_fields = ('title',)


@admin.register(Platform)
class PlatformAdmin(DeviceAdmin):
    list_display = ("title",)
    fields = ("title",)
    search_fields = ('title',)


@admin.register(OS)
class OSAdmin(DeviceAdmin):
    search_fields = ('title',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Device.objects.filter(type=Device.TYPE_PLATFORM)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Version)
class VersionAdmin(DeviceAdmin):
    search_fields = ('title',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Device.objects.filter(type=Device.TYPE_OS)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
