from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from apps.core.models import File


class FileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'display_image']
    search_fields = ['file']

    def file_name(self, obj):
        return getattr(obj.file, 'name', f"{obj.id}")
    file_name.short_description = _('file name')

    def display_image(self, obj):
        return mark_safe(f'<a href="{obj.file.url}" target="blank">open image</a>')


admin.site.register(File, FileAdmin)
