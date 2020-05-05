from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase

from apps.accounts.api.serializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer, UserProfileSerializer, \
    RegisterSerializer
from apps.accounts.models import UserProfile


class TokenObtainPairView(TokenViewBase):
    serializer_class = MyTokenObtainPairSerializer


class TokenRefreshView(TokenViewBase):
    serializer_class = MyTokenRefreshSerializer


def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return


def activate(request):
    verification_code = request.data['verification_code']


class UserProfileRetrieveAPIView(RetrieveModelMixin, GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
