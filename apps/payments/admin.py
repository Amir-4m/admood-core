from django.contrib import admin


from apps.accounts.admin_filter import UserFilter
from services.utils import AutoFilter
from .models import Transaction, Deposit


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ('user', 'value', 'created_time')
    search_fields = ('campaign__name', 'value')
    raw_id_fields = ('user',)
    readonly_fields = ('campaign', 'value')
    list_filter = (UserFilter, 'created_time', 'transaction_type')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def add_view(self, request, form_url='', extra_context=None):
        self.readonly_fields = ()
        return super().add_view(request, form_url, extra_context)


@admin.register(Deposit)
class PaymentAdmin(admin.ModelAdmin, AutoFilter):
    list_display = ['user', 'is_paid', 'updated_time', 'created_time']
    list_filter = (UserFilter, 'is_paid')
    search_fields = ('transaction_id',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
