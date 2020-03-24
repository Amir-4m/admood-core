from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import HelloView, GoogleAPIView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),

    path('google/', GoogleAPIView.as_view(), name="google"),
    path('hello/', HelloView.as_view(), name="hello"),
]
