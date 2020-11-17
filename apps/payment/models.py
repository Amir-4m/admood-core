import uuid

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from khayyam import JalaliDatetime

from admood_core import settings
from apps.campaign.models import Campaign
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
    TYPE_DEPOSIT = 'DEPOSIT'
    TYPE_WITHDRAW = 'WITHDRAW'
    TYPE_DEDUCT = 'DEDUCT'
    TYPE_REFUND = 'REFUND'
    TYPE_GIFT = 'GIFT'
    TYPE_PENALTY = 'PENALTY'

    TYPE_CHOICES = [
        (TYPE_DEPOSIT, _('Deposit')),
        (TYPE_WITHDRAW, _('Withdraw')),
        (TYPE_DEDUCT, _('Deduct')),
        (TYPE_REFUND, _('Refund')),
        (TYPE_GIFT, _('Gift')),
        (TYPE_PENALTY, _('Penalty')),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    value = models.IntegerField()
    description = models.TextField(blank=True)
    transaction_type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.PROTECT)
    created_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def balance(cls, user):
        return Transaction.objects.filter(user=user).aggregate(balance=Coalesce(Sum('value'), 0))['balance']

    @property
    def jalali_date(self):
        return JalaliDatetime(self.created_time).strftime('%A %d %B %Y')


class Payment(models.Model):
    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    updated_time = models.DateTimeField(_("updated time"), auto_now=True)
    invoice_number = models.UUIDField(_('uuid'), unique=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(_('transaction id'), unique=True, null=True, max_length=40)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_paid = models.NullBooleanField(_("is paid"))
    price = models.PositiveIntegerField(_('price'))
