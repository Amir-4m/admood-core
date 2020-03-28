from django.contrib import admin
from .models import (
    Platform,
    OS,
    OSVersion,
)


class OSAdmin(admin.ModelAdmin):
    list_display = ("platform", "name")


class OSVersionAdmin(admin.ModelAdmin):
    list_display = ("platform", "os", "version")

    def platform(self, obj):
        return obj.os.platform


admin.site.register(Platform)
admin.site.register(OS, OSAdmin)
admin.site.register(OSVersion, OSVersionAdmin)
