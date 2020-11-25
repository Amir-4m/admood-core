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
    CampaignContentSerializer, CampaignDuplicateSerializer, CampaignApproveSerializer, EstimateActionsSerializer)
from apps.campaign.models import Province, Campaign, CampaignContent
from apps.core.consts import CostModel
from apps.core.views import BaseViewSet
from apps.medium.models import Publisher, CostModelPrice


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
    def cost_model(self, request, *args, **kwargs):
        campaign = self.get_object()
        cost_model = kwargs.get('cost_model', CostModel.CPV)
        cp_price_max = CostModelPrice.max_price(campaign.final_publishers.all(), int(cost_model))
        return Response({'value': cp_price_max})

    @action(detail=False, methods=['post'], url_path='estimate-actions', serializer_class=EstimateActionsSerializer)
    def estimate_actions(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        publishers = serializer.data['publishers']
        categories = serializer.data['categories']

        publishers_by_categories = Publisher.get_by_categories(categories)
        publishers = {*publishers, *publishers_by_categories}

        budget = serializer.data['budget']

        cpv_price_max = CostModelPrice.max_price(publishers, CostModel.CPV)
        cpv_price_min = CostModelPrice.min_price(publishers, CostModel.CPV)

        cpc_price_max = CostModelPrice.max_price(publishers, CostModel.CPC)
        cpc_price_min = CostModelPrice.min_price(publishers, CostModel.CPC)

        cpi_price_max = CostModelPrice.max_price(publishers, CostModel.CPI)
        cpi_price_min = CostModelPrice.min_price(publishers, CostModel.CPI)

        cpr_price_max = CostModelPrice.max_price(publishers, CostModel.CPR)
        cpr_price_min = CostModelPrice.min_price(publishers, CostModel.CPR)

        cpv_min = budget // cpv_price_max if cpv_price_max else 0
        cpv_max = budget // cpv_price_min if cpv_price_min else 0

        cpc_min = budget // cpc_price_max if cpc_price_max else 0
        cpc_max = budget // cpc_price_min if cpc_price_min else 0

        cpi_min = budget // cpi_price_max if cpi_price_max else 0
        cpi_max = budget // cpi_price_min if cpi_price_min else 0

        cpr_min = budget // cpr_price_max if cpr_price_max else 0
        cpr_max = budget // cpr_price_min if cpr_price_min else 0

        data = {
            'cpv_min': cpv_min,
            'cpv_max': cpv_max,
            'cpc_min': cpc_min,
            'cpc_max': cpc_max,
            'cpi_min': cpi_min,
            'cpi_max': cpi_max,
            'cpr_min': cpr_min,
            'cpr_max': cpr_max,
        }

        return Response(data=data)


class ContentViewSet(BaseViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CampaignContentSerializer
    queryset = CampaignContent.objects.exclude(is_hidden=True)
    http_method_names = ['get', 'post', 'head', 'put']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        campaign_id = self.kwargs['campaign_id']
        return self.queryset.filter(campaign__owner=self.request.user, campaign__id=campaign_id)

    def perform_create(self, serializer):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_id'])
        serializer.save(campaign=campaign)
