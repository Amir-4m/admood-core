from django.urls import path

from .views import (MyTokenObtainPairView,
                    MyTokenRefreshView,
                    UserProfileViewSet,
                    RegisterUserByEmailAPIView,
                    VerifyUserAPIView,
                    PasswordResetAPIView,
                    PasswordResetConfirmAPIView, RegisterUserByPhoneAPIView, SetPasswordAPIView)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', MyTokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterUserByEmailAPIView.as_view()),
    path('register/phone/', RegisterUserByPhoneAPIView.as_view()),
    path('register/verify/', VerifyUserAPIView.as_view()),
    path('reset-pass/', PasswordResetAPIView.as_view()),
    path('reset-pass/confirm/', PasswordResetConfirmAPIView.as_view()),
    path('set-pass/', SetPasswordAPIView.as_view()),
    path('profile/', UserProfileViewSet.as_view({'get': 'retrieve',
                                                 'post': 'create',
                                                 'put': 'update',
                                                 'patch': 'partial_update'})),
    path('has_profile/', UserProfileViewSet.as_view({'get': 'has_profile'})),
]
