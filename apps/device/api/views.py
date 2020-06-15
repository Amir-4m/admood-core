import json
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.device.consts import ServiceProvider
from .serializers import (
    DeviceSerializer,
    PlatformSerializer,
    OSSerializer,
    OSVersionSerializer,
    ProviderSerializer
)
from ..models import Device, Platform, OS, Version


class DeviceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class PlatformViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class OSViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = OS.objects.all()
    serializer_class = OSSerializer


class OSVersionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Version.objects.all()
    serializer_class = OSVersionSerializer


class ProviderView(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProviderSerializer

    def list(self, request):
        serializer = self.serializer_class(ServiceProvider.SERVICE_PROVIDER_CHOICES, many=True)
        return Response(serializer.data)
