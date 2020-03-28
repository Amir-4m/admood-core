from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.campaign.api.serializers import ProvinceSerializer, CampaignSerializer, TargetDeviceSerializer, \
    ContentSerializer
from apps.campaign.models import Province, Campaign, CampaignTargetDevice, CampaignContent
from apps.core.views import BaseViewSet


class ProvinceViewSet(BaseViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer


class CampaignViewSet(BaseViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class TargetDeviceViewSet(BaseViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    # queryset = CampaignTargetDevice.objects.all()
    serializer_class = TargetDeviceSerializer

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return CampaignTargetDevice.objects.filter(campaign__id=campaign_id)


class ContentViewSet(BaseViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = CampaignContent.objects.all()
    serializer_class = ContentSerializer
