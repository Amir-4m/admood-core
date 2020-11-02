from django.contrib import admin

# Register your models here.
from apps.payment.models import Transaction, Payment


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'created_time']


@admin.register(Payment)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid', 'updated_time', 'created_time']
