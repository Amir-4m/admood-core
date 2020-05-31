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
    RegisterSerializer, VerifyUserSerializer)
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
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = User.get_by_email(email)
            if not user:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    is_active=False
                )
            else:
                user.set_password(password)

            # create and email user verification code
            user.email_verification_code()

        return Response(serializer.data)


class VerifyUserAPIView(GenericAPIView):
    serializer_class = VerifyUserSerializer

    def get(self, request):

        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            code = serializer.validated_data.get('code')
            if Verification.verify_user(user, code):
                return redirect(f'{SITE_URL}/{LOGIN_URI}')

        return redirect(f'{SITE_URL}/error/not-verified')


class ResetPasswordAPIView(GenericAPIView):
    serializer_class = RegisterSerializer

    def get(self, request):
        pass
        # todo: email user reset link

    def patch(self, request):
        user = User.get_by_email("email")
        serializer = self.serializer_class(instance=user, data=request.data, partial=True)



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
