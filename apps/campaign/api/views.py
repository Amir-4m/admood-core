from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.campaign.api.serializers import (
    ProvinceSerializer,
    CampaignSerializer,
    TargetDeviceSerializer,
    ContentSerializer
)
from apps.campaign.models import Province, Campaign, TargetDevice, Content
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


class TargetDeviceViewSet(BaseViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TargetDeviceSerializer

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return TargetDevice.objects.filter(campaign__owner=self.request.user, campaign__id=campaign_id)


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
