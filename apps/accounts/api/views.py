from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.api.serializers import (
    MyTokenObtainPairSerializer,
    MyTokenRefreshSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer, VerifyUserSerializer, RegisterPhoneSerializer,
)
from apps.accounts.models import UserProfile, Verification

User = get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


class RegisterUserAPIView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RegisterPhoneAPIView(GenericAPIView):
    serializer_class = RegisterPhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VerifyUserAPIView(GenericAPIView):
    serializer_class = VerifyUserSerializer
    queryset = Verification.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordResetConfirmAPIView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    queryset = User.objects.all()

    def get_verification(self):
        try:
            verification = Verification.objects.get(uuid=self.request.query_params.get('rc'))
            if verification.is_valid:
                return verification
        except:
            raise Http404

    def get(self, request):
        if self.get_verification():
            return Response()

    def put(self, request):
        verification = self.get_verification()
        user = verification.user
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        verification.verify()
        return Response({'email': user.email})


class UserProfileViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        try:
            return self.get_queryset().get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return None

    @action(detail=False, methods=['get'])
    def has_profile(self, request):
        data = {
            'has_profile': self.queryset.filter(user=request.user).exists()
        }
        return Response(data=data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({
            'phone_number': request.user.phone_number,
            'email': request.user.email
        })
