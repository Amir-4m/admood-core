from django.contrib import admin

from .forms import PublisherForm
from .models import (
    Category,
    Publisher,
    CostModelPrice,
)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'medium']
    search_fields = ['name']
    form = PublisherForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'medium', 'display_text', 'ref_id']


@admin.register(CostModelPrice)
class CostModelPriceAdmin(admin.ModelAdmin):
    list_display = ['medium', 'grade']
