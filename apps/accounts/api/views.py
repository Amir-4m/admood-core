from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase

from apps.accounts.api.serializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer, UserProfileSerializer
from apps.accounts.models import UserProfile


class TokenObtainPairView(TokenViewBase):
    serializer_class = MyTokenObtainPairSerializer


class TokenRefreshView(TokenViewBase):
    serializer_class = MyTokenRefreshSerializer


class HelloView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class LoginAPIView(APIView):

    def mobile_authenticate(self):
        pass

    def email_authenticate(self):
        pass

    def post(self, request):
        pass

