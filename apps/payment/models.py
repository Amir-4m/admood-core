from django.db import models

from admood_core import settings


class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # payment =
    reference_number = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    # vat =
    due_date = models.DateTimeField()
    total = models.DecimalField(max_digits=20, decimal_places=2)
    invoice_status = models.CharField(max_length=20)
    payment_type = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)
