from django.contrib import admin
from .models import (
    Category,
    MediumCategoryDisplayText,
    Publisher,
)


class PublisherAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(Category)
admin.site.register(MediumCategoryDisplayText)
admin.site.register(Publisher, PublisherAdmin)
