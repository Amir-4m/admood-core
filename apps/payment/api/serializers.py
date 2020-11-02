from rest_framework import serializers

from apps.payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'invoice_number', 'is_paid', 'redirect_url', 'price', 'created_time', 'updated_time')
        extra_kwargs = {
            'redirect_url': {'write_only': True}
        }
