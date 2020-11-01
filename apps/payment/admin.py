from django.contrib import admin

# Register your models here.
from apps.payment.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'created_time')
    search_fields = ('user__username', 'value')
    list_filter = ('created_time',)
