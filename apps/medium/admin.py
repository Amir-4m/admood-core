from django.contrib import admin

from services.utils import AutoFilter
from .forms import PublisherForm
from .admin_filter import CategoriesFilter, CostModelPriceFilter
from .models import (
    Category,
    Publisher,
    CostModelPrice,
)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ['name', 'medium', 'status', 'is_enable', 'created_time', 'updated_time']
    list_filter = [CategoriesFilter, CostModelPriceFilter, 'medium', 'status', 'is_enable']
    search_fields = ['name']
    fields = ['name', 'medium', 'is_enable', 'status', 'categories', 'cost_models',
              'extra_data', 'description', 'url', 'ref_id']
    filter_horizontal = ['cost_models', 'categories']
    readonly_fields = ['medium', 'ref_id', 'url']
    form = PublisherForm

    def has_add_permission(self, request):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'medium', 'display_text', 'ref_id', 'created_time', 'updated_time']
    search_fields = ['title', 'display_text']
    list_filter = ('medium',)


@admin.register(CostModelPrice)
class CostModelPriceAdmin(admin.ModelAdmin):
    list_display = (
        'medium', 'grade', 'cost_model',
        'advertiser_price', 'publisher_price',
        'created_time', 'updated_time'
    )
    search_fields = ('grade',)
    list_filter = ('medium',)
