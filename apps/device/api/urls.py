from django.urls import path

from .views import PlatformViewSet, OSViewSet, OSVersionViewSet, ProviderView

urlpatterns = [
    path('platforms/', PlatformViewSet.as_view({'get': 'list'})),
    path('os/', OSViewSet.as_view({'get': 'list'})),
    path('os_versions/', OSVersionViewSet.as_view({'get': 'list'})),
    path('providers/', ProviderView.as_view({'get': 'list'})),
]
