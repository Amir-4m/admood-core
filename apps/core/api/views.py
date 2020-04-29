from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.api.serializers import FileSerializer
from apps.core.models import File


class FileViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer
    queryset = File.objects.all()
