from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.medium.api.serializers import MediumSerializer, PublisherSerializer, CategorySerializer
from apps.medium.models import Publisher, Category
from ..consts import Medium


class MediumViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MediumSerializer

    def list(self, request):
        serializer = self.serializer_class(Medium.MEDIUM_CHOICES, many=True)
        return Response(serializer.data)


class PublisherViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PublisherSerializer
    queryset = Publisher.approved_objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        medium = self.request.query_params.get('medium')
        if medium is not None:
            queryset = queryset.filter(medium=medium)
        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(categories=category)

        return queryset


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        medium = self.request.query_params.get('medium')
        if medium is not None:
            queryset = queryset.filter(medium=medium)
        return queryset
