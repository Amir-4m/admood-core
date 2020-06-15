from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.medium.api.serializers import MediumSerializer, PublisherSerializer, MediumCategorySerializer
from apps.medium.models import Publisher, MediumCategory
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
    queryset = Publisher.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        medium = self.request.query_params.get('medium')
        if medium is not None:
            queryset = queryset.filter(medium=medium)
        return queryset


class MediumCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MediumCategorySerializer
    queryset = MediumCategory.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        medium = self.request.query_params.get('medium')
        if medium is not None:
            queryset = queryset.filter(medium=medium)
        return queryset
