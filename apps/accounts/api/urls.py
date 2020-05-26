from django.urls import path

from apps.accounts.api.views import confirm_registration_code
from .views import TokenObtainPairView, TokenRefreshView, UserProfileViewSet, RegisterAPIView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterAPIView.as_view(), name="register"),
    path('verify/', confirm_registration_code, name="verify"),
    path('profile/', UserProfileViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'put': 'update',
        'patch': 'partial_update'
    })
         ),
    path('has_profile/', UserProfileViewSet.as_view({'get': 'has_profile'})),
]
