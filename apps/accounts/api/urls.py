from django.urls import path

from .views import (MyTokenObtainPairView,
                    MyTokenRefreshView,
                    UserProfileViewSet,
                    RegisterUserByEmailAPIView,
                    VerifyUserAPIView,
                    PasswordResetAPIView,
                    PasswordResetConfirmAPIView, RegisterUserByPhoneAPIView, SetPasswordAPIView, ChangePasswordAPIView,
                    SetPhoneNumberAPIView, VerifyPhoneNumberAPIView)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', MyTokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterUserByEmailAPIView.as_view(), name='register_user_by_email'),
    path('register/phone/', RegisterUserByPhoneAPIView.as_view(), name='register_user_by_phone'),
    path('register/verify/', VerifyUserAPIView.as_view(), name='register_verify'),
    path('reset-pass/', PasswordResetAPIView.as_view(), name='reset_pass'),
    path('reset-pass/confirm/', PasswordResetConfirmAPIView.as_view(), name='reset_pass_confirm'),
    path('set-pass/', SetPasswordAPIView.as_view(), name='set_pass'),
    path('profile/', UserProfileViewSet.as_view({'get': 'retrieve',
                                                 'post': 'create',
                                                 'put': 'update',
                                                 'patch': 'partial_update'}), name='user_profile'),
    path('has_profile/', UserProfileViewSet.as_view({'get': 'has_profile'})),
    path('change-pass/', ChangePasswordAPIView.as_view()),
    path('phone-number/', SetPhoneNumberAPIView.as_view()),
    path('phone-number/verify/', VerifyPhoneNumberAPIView.as_view()),
]
