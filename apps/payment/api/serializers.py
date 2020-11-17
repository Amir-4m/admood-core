from rest_framework import serializers

from apps.payment.models import Payment, Transaction


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'invoice_number', 'is_paid', 'price', 'created_time', 'updated_time')


class TransactionSerializer(serializers.ModelSerializer):
    created_time = serializers.ReadOnlyField(source='jalali_date')

    class Meta:
        model = Transaction
        fields = ('id', 'value', 'description', 'transaction_type', 'campaign', 'created_time')
