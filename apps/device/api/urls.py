from django.urls import path

from .views import DeviceViewSet, PlatformViewSet, OSViewSet, OSVersionViewSet, ProviderView

urlpatterns = [
    path('devices/', DeviceViewSet.as_view({'get': 'list'})),
    path('platforms/', PlatformViewSet.as_view({'get': 'list'})),
    path('os/', OSViewSet.as_view({'get': 'list'})),
    path('os_versions/', OSVersionViewSet.as_view({'get': 'list'})),
    path('providers/', ProviderView.as_view({'get': 'list'})),
]
