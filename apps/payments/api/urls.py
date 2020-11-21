from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BalanceAPIView, DepositViewSet, TransactionViewSet

urlpatterns = [
    path('balance/', BalanceAPIView.as_view(), name="balance"),
]

router = DefaultRouter()
router.register('deposit', DepositViewSet)
router.register('transaction', TransactionViewSet)

urlpatterns += router.urls
