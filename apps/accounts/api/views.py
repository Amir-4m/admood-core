from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import redirect
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase

from admood_core.settings import SITE_URL, LOGIN_URL
from apps.accounts.api.serializers import (
    MyTokenObtainPairSerializer,
    MyTokenRefreshSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    VerifyUserSerializer,
    ResetPasswordSerializer,
    ForgetPasswordSerializer,
)
from apps.accounts.models import UserProfile, Verification

User = get_user_model()


class TokenObtainPairView(TokenViewBase):
    serializer_class = MyTokenObtainPairSerializer


class TokenRefreshView(TokenViewBase):
    serializer_class = MyTokenRefreshSerializer


class RegisterUserAPIView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VerifyUserAPIView(GenericAPIView):
    serializer_class = VerifyUserSerializer
    queryset = Verification.objects.all()

    def get_object(self):
        code = self.request.query_params.get('code')
        try:
            return Verification.objects.get(code=code)
        except:
            raise redirect(f'{SITE_URL}/error/not-verified')

    def get(self, request):
        verification = self.get_object()
        if not verification.validate():
            return redirect(f'{SITE_URL}/error/not-verified')
        verification.verify()
        verification.user.verify()
        return redirect(f'{SITE_URL}/{LOGIN_URL}')


class ForgetPasswordAPIView(GenericAPIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ResetPasswordAPIView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def get_object(self):
        uuid = self.request.query_params.get('uuid')
        try:
            return Verification.get(uuid).user
        except:
            raise Http404

    def get(self, request):
        user = self.get_object()
        return Response({'email': user.email})

    def put(self, request):
        user = self.get_object()
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
