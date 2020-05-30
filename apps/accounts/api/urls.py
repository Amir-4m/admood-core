from django.urls import path

from .views import TokenObtainPairView, TokenRefreshView, UserProfileViewSet, RegisterUserAPIView, VerifyUserAPIView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterUserAPIView.as_view()),
    path('register/verify/', VerifyUserAPIView.as_view()),
    path('profile/', UserProfileViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'put': 'update',
        'patch': 'partial_update'
    })
         ),
    path('has_profile/', UserProfileViewSet.as_view({'get': 'has_profile'})),
]
