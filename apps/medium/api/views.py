from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.throttling import AnonRateThrottle

from apps.medium.api.serializers import MediumSerializer, PublisherSerializer, CategorySerializer
from apps.medium.models import Publisher, Category
from ..consts import Medium
from ..tasks import update_telegram_publishers_task


class MediumViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MediumSerializer

    def list(self, request):
        serializer = self.serializer_class(Medium.MEDIUM_CHOICES, many=True)
        return Response(serializer.data)


class PublisherViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PublisherSerializer
    queryset = Publisher.approved_objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'extra_data__member_no', 'extra_data__view_efficiency', 'extra_data__tag']

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            cost_models__isnull=False
        ).prefetch_related('categories')

        medium = self.request.query_params.get('medium', '')
        if medium.isdigit():
            queryset = queryset.filter(medium=medium)
        category = self.request.query_params.get('category', '')
        if category.isdigit():
            queryset = queryset.filter(categories=category)

        return queryset


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().filter(publisher__categories__campaign__isnull=False).distinct()
        medium = self.request.query_params.get('medium')
        if medium is not None:
            queryset = queryset.filter(medium=medium)
        return queryset


class UpdatePublisherViewSet(viewsets.ViewSet):
    throttle_classes = (AnonRateThrottle,)

    def list(self, request, *args, **kwargs):
        update_telegram_publishers_task.delay()
        return Response()
