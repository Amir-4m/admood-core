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


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Email address must be unique."}
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            is_active=False
        )

        user.email_verification_code()

        return user

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {"password": "password mismatch."}
            )
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

    def validate(self, attrs):
        user = attrs.get['user']
        code = attrs.get['code']

        valid_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
        if Verification.objects.filter(user=user,
                                       code=code,
                                       verified_time__isnull=True,
                                       created_time__gte=valid_time
                                       ).exists():
            return attrs

        raise serializers.ValidationError(
            "invalid verification."
        )


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
