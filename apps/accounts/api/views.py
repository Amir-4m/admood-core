from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
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
    RegisterUserByEmailSerializer,
    SetPasswordSerializer,
    PasswordResetSerializer,
    RegisterUserByPhoneSerializer,
    VerifyUserSerializer, ChangePasswordSerializer, SetPhoneNumberSerializer, VerifyPhoneNumberSerializer,
)
from apps.accounts.models import UserProfile, Verification

User = get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


class RegisterUserByEmailAPIView(GenericAPIView):
    serializer_class = RegisterUserByEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RegisterUserByPhoneAPIView(GenericAPIView):
    serializer_class = RegisterUserByPhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VerifyUserAPIView(GenericAPIView):
    serializer_class = VerifyUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = Verification.verify_user_by_email(verify_code=serializer.data["rc"])
        if verification:
            verification.user.verify()
            verification.user.save()
            return Response()
        raise NotFound


class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordResetConfirmAPIView(GenericAPIView):
    serializer_class = SetPasswordSerializer
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


class SetPasswordAPIView(GenericAPIView):
    serializer_class = SetPasswordSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def put(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()


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


class ChangePasswordAPIView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()


class SetPhoneNumberAPIView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = SetPhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.send_verification_sms(phone_number=serializer.validated_data['phone_number'])
        return Response(data=serializer.data)


class VerifyPhoneNumberAPIView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = VerifyPhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        phone_number = serializer.validated_data['phone_number']
        verify_code = serializer.validated_data['verify_code']
        verification = Verification.verify_phone_number(
            user=user,
            phone_number=phone_number,
            verify_code=verify_code,
        )
        if verification:
            user.phone_number = phone_number
            user.save()
            return Response({'phone_number': phone_number})
        raise NotFound
