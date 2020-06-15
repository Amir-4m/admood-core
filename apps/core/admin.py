from django.contrib import admin

from apps.core.models import File


class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file']


admin.site.register(File, FileAdmin)
