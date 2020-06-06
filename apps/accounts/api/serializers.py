import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile, Verification

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())

        return data


class MyTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())

        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, write_only=True)
    confirm_password = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        fields = [
            "email",
            "password",
            "confirm_password"
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"password": "password mismatch."}
            )

        if Verification.objects.filter(user__email=attrs['email'], verified_time__isnull=False).exists():
            raise serializers.ValidationError({'email': 'user with this email already exists.'})

        return attrs


class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return User.objects.get(email=data)


class VerifyUserSerializer(serializers.ModelSerializer):
    user = UserRelatedField(queryset=User.objects.all())
    code = serializers.IntegerField()

    class Meta:
        model = Verification
        fields = ['user', 'code']


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {'email': 'invalid email address.'})

        return value

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        user.email_reset_password()


class ResetPasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "password mismatch."})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserProfile
        exclude = ['id', 'created_time', 'updated_time']
        read_only_fields = ['status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(
            {
                'phone_number': instance.user.phone_number,
                'email': instance.user.email
            }
        )
        return data

    def update(self, instance, validated_data):
        if instance.status == UserProfile.STATUS_APPROVED:
            raise ValidationError({"non_field_errors": ["approved profiles are not editable"]})
        return super().update(instance, validated_data)

    def create(self, validated_data):
        if UserProfile.objects.filter(user=validated_data['user']).exists():
            raise ValidationError({"non_field_errors": ["user profile already exists"]})
        return super().create(validated_data)


class RealProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'type',
            'status',
            'national_id',
            'image',
            'bio',
            'address',
        ]
        read_only_fields = ['status']


class LegalProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserProfile
        fields = [
            'company_name',
            'type',
            'status',
            'image',
            'bio',
            'address',
            'eco_code',
            'register_code'
        ]
        read_only_fields = ['status']
