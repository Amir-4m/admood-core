from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.medium.api.serializers import MediumSerializer
from ..consts import Medium


class MediumViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MediumSerializer

    def list(self, request):
        serializer = self.serializer_class(Medium.MEDIUM_CHOICES, many=True)
        return Response(serializer.data)
