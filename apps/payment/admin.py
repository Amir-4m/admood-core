from django.contrib import admin

# Register your models here.
from apps.payment.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'date_time', 'status']
