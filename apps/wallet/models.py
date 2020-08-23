from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Transaction(models.Model):
    PENDING = '0'
    SUCCESS = '1'
    FAILED = '2'

    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (SUCCESS, 'success'),
        (FAILED, 'failed')
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    value = models.IntegerField()
    date_time = models.DateTimeField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    description = models.TextField(blank=True)


def balance(user):
    return Transaction.objects.filter(user=user).aggregate(balance=Coalesce(Sum('value'), 0))['balance']
