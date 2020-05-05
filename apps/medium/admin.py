from django.contrib import admin
from .models import (
    Category,
    MediumCategory,
    Publisher,
)


class PublisherAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(Category)
admin.site.register(MediumCategory)
admin.site.register(Publisher, PublisherAdmin)
