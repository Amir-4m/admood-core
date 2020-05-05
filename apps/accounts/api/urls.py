from django.urls import path

from .views import TokenObtainPairView, TokenRefreshView, register, activate

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', register, name="register"),
    path('activate/', activate, name="activate"),
]
