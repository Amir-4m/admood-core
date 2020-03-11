from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import HelloView, GoogleView

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path('google/', GoogleView.as_view(), name="google"),
    path('hello/', HelloView.as_view(), name="hello"),
]