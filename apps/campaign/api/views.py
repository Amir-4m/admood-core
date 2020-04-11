from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.campaign.api.serializers import (
    ProvinceSerializer,
    CampaignSerializer,
    DeviceSerializer,
    ContentSerializer,
    CampaignStatusSerializer)
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
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        campaign = self.get_object()

        if campaign.status == Campaign.STATUS_APPROVED:
            return Response("Approved campaigns cannot be edited!")

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="status")
    def status(self, request, *args, **kwargs):
        self.serializer_class = CampaignStatusSerializer
        return super().update(request, *args, **kwargs)


class TargetDeviceViewSet(BaseViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return self.queryset.filter(campaign__owner=self.request.user, campaign__id=campaign_id)


class ContentViewSet(BaseViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return self.queryset.filter(campaign__owner=self.request.user, campaign__id=campaign_id)
