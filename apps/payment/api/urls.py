from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BalanceAPIView, PaymentViewSet

urlpatterns = [
    path('balance/', BalanceAPIView.as_view(), name="balance"),
]

router = DefaultRouter()
router.register('', PaymentViewSet)

urlpatterns += router.urls
