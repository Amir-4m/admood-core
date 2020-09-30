from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from admood_core import settings
from apps.core.consts import Bank


# class Invoice(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     # payment =
#     reference_number = models.CharField(max_length=20)
#     description = models.TextField(null=True, blank=True)
#     balance = models.DecimalField(max_digits=20, decimal_places=2)
#     # vat =
#     due_date = models.DateTimeField()
#     total = models.DecimalField(max_digits=20, decimal_places=2)
#     invoice_status = models.CharField(max_length=20)
#     payment_type = models.CharField(max_length=20)
#     created_time = models.DateTimeField(auto_now_add=True)
#
#
# class Payment(models.Model):
#     bank_name = models.CharField(max_length=20, choices=Bank.BANK_CHOICES)
#     transaction_no = models.CharField(max_length=50)
#     status = models.CharField(max_length=20)
#     amount = models.DecimalField(max_length=20, decimal_places=2)
#     card_no = models.CharField(max_length=20)
#     ip = models.IPAddressField()
#     created_time = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    PENDING = 0
    SUCCESS = 1
    FAILED = 2

    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (SUCCESS, 'success'),
        (FAILED, 'failed')
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    value = models.IntegerField()
    date_time = models.DateTimeField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    description = models.TextField(blank=True)

    @classmethod
    def balance(cls, user):
        return Transaction.objects.filter(user=user).aggregate(balance=Coalesce(Sum('value'), 0))['balance']
