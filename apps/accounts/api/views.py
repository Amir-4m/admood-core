from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from admood_core import settings
from apps.accounts.api.serializers import (
    MyTokenObtainPairSerializer,
    MyTokenRefreshSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer, RegisterPhoneSerializer,
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
    queryset = Verification.objects.all()

    def get_object(self):
        code = self.request.data["code"]
        try:
            return self.queryset.objects.get(
                code=code,
                type=Verification.VERIFY_TYPE_EMAIL,
                verified_time__isnull=True,
                created_time__gt=timezone.now() - timezone.timedelta(minutes=settings.USER_VERIFICATION_LIFETIME),
            )
        except:
            raise NotFound

    def post(self, request):
        verification = self.get_object()
        verification.verify()
        verification.save()
        verification.user.verify()
        return Response()


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
        verification = Verification.get_valid(
            verify_code=self.request.query_params.get('rc'),
            verify_type=Verification.VERIFY_TYPE_EMAIL
        )
        if verification:
            return verification
        raise NotFound

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
        verification.save()
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
            'has_profile': self.queryset.filter(user=request.user).exists(),
            'has_password': request.user.has_usable_password(),
        }
        return Response(data=data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({
            'phone_number': request.user.phone_number,
            'email': request.user.email,
            'has_password': request.user.has_usable_password(),
        })
