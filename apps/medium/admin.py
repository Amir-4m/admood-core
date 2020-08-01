from django.contrib import admin

from .forms import PublisherForm
from .models import (
    Category,
    Category,
    Publisher,
)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'medium']
    search_fields = ['name']
    form = PublisherForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'medium', 'display_text', 'reference_id']
