from django.urls import path

from .views import TokenObtainPairView, TokenRefreshView, UserProfileViewSet, register, activate

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', register, name="register"),
    path('activate/', activate, name="activate"),
    path('profile/', UserProfileViewSet.as_view({'get': 'retrieve', 'post': 'create', 'put': 'update'})),
    path('has_profile/', UserProfileViewSet.as_view({'get': 'has_profile'})),
]
