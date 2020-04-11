from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.campaign.api.serializers import (
    ProvinceSerializer,
    CampaignSerializer,
    DeviceSerializer,
    ContentSerializer
)
from apps.campaign.models import Province, Campaign, Device, Content
from apps.core.views import BaseViewSet


class ProvinceViewSet(BaseViewSet,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer


class CampaignViewSet(BaseViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CampaignSerializer

    def get_queryset(self):
        return Campaign.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        campaign = self.get_object()

        if campaign.status == Campaign.STATUS_APPROVED and 'is_active' not in request.data:
            return Response("Approved campaigns cannot be updated!")

        return super().update(request, *args, **kwargs)


class TargetDeviceViewSet(BaseViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DeviceSerializer

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return Device.objects.filter(campaign__owner=self.request.user, campaign__id=campaign_id)


class ContentViewSet(BaseViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ContentSerializer

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return Content.objects.filter(campaign__owner=self.request.user, campaign__id=campaign_id)
