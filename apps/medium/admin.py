from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from django_json_widget.widgets import JSONEditorWidget

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
    form = PublisherForm
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_display = ['name', 'medium', 'status', 'is_enable', 'created_time', 'updated_time']
    list_filter = [CategoriesFilter, CostModelPriceFilter, 'medium', 'status', 'is_enable']
    search_fields = ['name']
    fields = ['name', 'medium', 'is_enable', 'status', 'categories', 'cost_models',
              'extra_data', 'description', 'url', 'ref_id']
    filter_horizontal = ['cost_models', 'categories']
    readonly_fields = ['medium', 'ref_id', 'url']
    radio_fields = {'status': admin.VERTICAL}

    def has_add_permission(self, request):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'medium', 'display_text', 'ref_id', 'created_time', 'updated_time', 'number_of_publishers'
    ]
    search_fields = ['title', 'display_text']
    list_filter = ('medium',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _publisher_count=Count("publisher", distinct=True),
        )
        return queryset

    def number_of_publishers(self, obj):
        return obj._publisher_count
    number_of_publishers.short_description = _('number of publishers')
    number_of_publishers.admin_order_field = '_publisher_count'


@admin.register(CostModelPrice)
class CostModelPriceAdmin(admin.ModelAdmin):
    list_display = (
        'medium', 'grade', 'cost_model',
        'advertiser_price', 'publisher_price',
        'created_time', 'updated_time'
    )
    search_fields = ('grade',)
    list_filter = ('medium',)
