from django.contrib import admin
from .models import (
    Category,
    Category,
    Publisher,
)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'medium', 'display_text', 'reference_id']
