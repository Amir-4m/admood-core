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
    list_filter = ['medium']
    search_fields = ['name', 'medium']
    fields = ["name", "medium", "categories", "cost_models", "description", "is_enable", "url", "ref_id"]
    filter_horizontal = ['cost_models', 'categories']
    readonly_fields = ['medium', 'ref_id', 'url']
    form = PublisherForm

    def has_add_permission(self, request):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'medium', 'display_text', 'ref_id']
    search_fields = ['title']
    list_filter = ('medium',)


@admin.register(CostModelPrice)
class CostModelPriceAdmin(admin.ModelAdmin):
    list_display = ('medium', 'grade')
    list_filter = ('medium',)
