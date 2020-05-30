import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase

from admood_core.settings import SITE_URL, LOGIN_URI
from apps.accounts.api.serializers import (
    MyTokenObtainPairSerializer,
    MyTokenRefreshSerializer,
    UserProfileSerializer,
    RegisterSerializer)
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
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)


class VerifyUserAPIView(GenericAPIView):
    def get(self, request):

        email = request.query_params.get('email')
        code = request.query_params.get('code')
        valid_time = datetime.datetime.now() - datetime.timedelta(days=90)

        if not (email or code):
            return redirect(f'{SITE_URL}/error/not-verified')
        try:
            verification = Verification.objects.get(
                user__email=email,
                code=code,
                verified_time__isnull=True,
                created_time__gte=valid_time
            )
        except Verification.DoesNotExist:
            return redirect(f'{SITE_URL}/error/not-verified')

        verification.verified_time = datetime.datetime.now()
        verification.user.is_active = True
        verification.user.save()
        verification.save()

        return redirect(f'{SITE_URL}/{LOGIN_URI}')


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
            'username': request.user.username,
            'phone_number': request.user.phone_number,
            'email': request.user.email
        })
