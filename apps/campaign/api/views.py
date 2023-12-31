from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import ugettext_lazy as _

from apps.campaign.api.serializers import (
    ProvinceSerializer,
    CampaignSerializer,
    CampaignContentSerializer, CampaignDuplicateSerializer, EstimateActionsSerializer,
    CampaignReferenceSerializer, CampaignDashboardReportSerializer, CampaignEnableSerializer
)
from apps.campaign.models import Province, Campaign, CampaignContent, CampaignReference
from apps.core.consts import CostModel
from apps.core.views import BaseViewSet
from apps.medium.models import CostModelPrice
from apps.payments.models import Transaction


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
        if self.request.user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], serializer_class=CampaignEnableSerializer)
    def enable(self, request, *args, **kwargs):
        instance = self.get_object()
        is_enable = request.data.get('is_enable', instance.is_enable)
        serializer = self.get_serializer(instance, data={'is_enable': is_enable})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Campaign.STATUS_DRAFT:
            raise ValidationError({'status': _('Ensure this campaign is a draft.')})
        if instance.contents.filter(is_hidden=False).count() == 0:
            raise ValidationError(
                {'status': _('At least one content for campaign must be existed to approve campaign!')}
            )
        if instance.total_budget > Transaction.balance(instance.owner):
            raise ValidationError({'total_budget': _('wallet balance is lower than total budget!')})

        instance.status = Campaign.STATUS_WAITING
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], serializer_class=CampaignDuplicateSerializer)
    def duplicate(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # Evaluate max model price based on campaign's publishers
    @action(detail=True, methods=['get'], url_path=r'cost_model/(?P<cost_model>[^/.]+)')
    def cost_model(self, request, *args, **kwargs):
        campaign = self.get_object()

        publishers = campaign.get_all_publishers(
            campaign.publishers.values_list('id', flat=True),
            campaign.categories.all()
        )
        cost_model = kwargs.get('cost_model', CostModel.CPV)

        return Response({'value': CostModelPrice.max_price(publishers, int(cost_model))})

    # Estimate campaign model prices like cpv, cpc and ... based on selected publishers or categories
    @action(detail=False, methods=['post'], url_path='estimate-actions', serializer_class=EstimateActionsSerializer)
    def estimate_actions(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        publishers = serializer.data['publishers']
        categories = serializer.data['categories']

        publishers = Campaign.get_all_publishers(publishers, categories)

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

    @action(detail=True, methods=['get'], serializer_class=CampaignReferenceSerializer)
    def references(self, request, *args, **kwargs):
        instance = self.get_object()
        campaign_references = instance.campaignreference_set.all()
        serializer = self.get_serializer(campaign_references, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='dashboard-report',
        serializer_class=CampaignDashboardReportSerializer
    )
    def dashboard_report(self, request, *args, **kwargs):
        data = request.query_params
        context = dict(owner_id=request.user.id)
        if request.user.is_superuser:
            context = {}

        serializer = CampaignDashboardReportSerializer(
            data=data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


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
        if self.request.user.is_superuser:
            return self.queryset.filter(campaign__id=self.kwargs['campaign_id'])
        return self.queryset.filter(campaign__owner=self.request.user, campaign__id=self.kwargs['campaign_id'])


class CampaignReferenceViewSet(viewsets.GenericViewSet):
    queryset = CampaignReference.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CampaignReferenceSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(campaign__owner=self.request.user)

    @method_decorator(cache_page(60 * 10))
    @action(detail=True, methods=['get'], url_path='report')
    def report(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

