from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.campaign.api.serializers import (
    ProvinceSerializer,
    CampaignSerializer,
    CampaignContentSerializer, CampaignDuplicateSerializer, CampaignApproveSerializer)
from apps.campaign.models import Province, Campaign, CampaignContent
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
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"])
    def enable(self, request, *args, **kwargs):
        instance = self.get_object()
        is_enable = request.data.get('is_enable', instance.is_enable)
        serializer = self.get_serializer(instance, data={'is_enable': is_enable}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], serializer_class=CampaignApproveSerializer)
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'status': Campaign.STATUS_WAITING}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=CampaignDuplicateSerializer)
    def duplicate(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path=r'cost_model/(?P<cost_model>[^/.]+)')
    def cost_model(self, request, cost_model, pk=None):
        # todo: calculate min of cost model price
        return Response({'value': 300})


class ContentViewSet(BaseViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CampaignContentSerializer
    queryset = CampaignContent.objects.all()
    http_method_names = ['get', 'post', 'head', 'put']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return self.queryset.filter(campaign__owner=self.request.user, campaign__id=campaign_id)

    def perform_create(self, serializer):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'])
        serializer.save(campaign=campaign)
