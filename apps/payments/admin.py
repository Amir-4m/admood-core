from django.contrib import admin

# Register your models here.
from .models import Transaction, Deposit


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'created_time')
    search_fields = ('user__username', 'value')
    list_filter = ('created_time',)


@admin.register(Deposit)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid', 'updated_time', 'created_time']
    list_filter = ('is_paid',)
    search_fields = ('transaction_id',)
