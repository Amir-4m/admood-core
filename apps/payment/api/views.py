from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.payment.models import Transaction


class BalanceAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        balance = Transaction.balance(request.user)
        data = {'balance': balance}
        return Response(data=data)


class GatewayListAPIView(APIView):
    def get(self, request):
        pass
