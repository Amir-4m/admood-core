from django.contrib import admin

# Register your models here.
from apps.payment.models import Transaction, Payment


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'created_time')
    search_fields = ('user__username', 'value')
    list_filter = ('created_time',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid', 'updated_time', 'created_time']
    list_filter = ('is_paid',)
    search_fields = ('transaction_id',)
