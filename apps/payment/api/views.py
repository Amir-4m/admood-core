import logging

from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.payment.api.serializers import PaymentSerializer
from apps.payment.models import Transaction, Payment
from apps.payment.utils import payment_request

logger = logging.getLogger(__name__)


class BalanceAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        balance = Transaction.balance(request.user)
        data = {'balance': balance}
        return Response(data=data)


class PaymentViewSet(ListModelMixin,
                     RetrieveModelMixin,
                     GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super(PaymentViewSet, self).get_queryset()
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.id)

    @action(methods=['post'], detail=False, url_path='charge')
    def charge(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = Payment.objects.create(
            price=data['price'],
            redirect_url=data['redirect_url'],
            user=request.user

        )
        try:
            # creating order in payment system
            order_response = payment_request(
                'orders',
                'post',
                data={
                    'price': obj.price,
                    'service_reference': str(obj.invoice_number),
                    'is_paid': obj.is_paid,
                    "properties": {
                        "redirect_url": request.build_absolute_uri(reverse('payment-done')),
                    }
                }
            )
            transaction_id = order_response.json().get('transaction_id')
        except Exception as e:
            logger.error(
                f'[message: error calling payment with endpoint orders and action post {e}]-[payment: {obj.id}]'
            )
            raise ParseError('error occurred in creating order')

        obj.transaction_id = transaction_id
        obj.save()

        return Response({'payment': obj.id, 'gateways': order_response.json().get('gateways')})

    @action(methods=['post'], detail=True, url_path='gateway')
    def gateway(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.is_paid is True:
            raise ValidationError("payment has been done already!")
        elif payment.is_paid is False:
            raise ValidationError("payment has not been done successfully!")

        gateway = request.data.get('gateway')
        if gateway is None:
            raise ValidationError("gateway is required")
        try:
            # set gateway for order and get gateway url
            response = payment_request(
                'purchase/gateway',
                'post',
                data={'order': str(payment.invoice_number), 'gateway': gateway}
            )
        except Exception as e:
            logger.error(
                f'[message: error calling payment with endpoint purchase/gateway and action post {e}]-[payment: {payment.id}]'
            )
            raise ParseError('error occurred in setting gateway')
        return Response(data=response.json())
