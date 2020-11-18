from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .models import Deposit, Transaction


class PaymentView(View):
    def get(self, request, *args, **kwargs):
        transaction_id = request.GET.get('transaction_id')
        purchase_verified = request.GET.get('purchase_verified')
        if purchase_verified is None:
            return HttpResponse('وضعیت سفارش نا معتبر می باشد !')

        purchase_verified = purchase_verified.lower().strip()
        with transaction.atomic():
            try:
                order = Deposit.objects.select_for_update('self').get(
                    transaction_id=transaction_id,
                    is_paid=None
                )
            except Deposit.DoesNotExist:
                return HttpResponse('سفارشی یافت نشد !')

            if purchase_verified == 'true':
                html = 'payment/payment_done.html'
                order.is_paid = True

            else:
                html = 'payment/payment_failed.html'
                order.is_paid = False

            order.save()
            if order.is_paid is True:
                Transaction.objects.create(
                    user=order.user,
                    value=order.price,
                    description=f" {order.invoice_number} شماره پیگیری شارژ کیف پول ",
                    transaction_type=Transaction.TYPE_DEPOSIT
                )
        context = {
            "redirect_url": settings.PAYMENT_REDIRECT_URL,
            "purchase_verified": purchase_verified,
            "price": order.price,
            "invoice_number": order.invoice_number
        }
        return render(request, html, context)
