import logging

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from apps.accounts.models import UserProfile

User = get_user_model()
logger = logging.getLogger(__file__)


class LifeTimeTokenSerializer:

    def validate(self, attrs):
        # adding lifetime to data
        data = super().validate(attrs)
        data['lifetime'] = int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds())
        return data


class LifeTimeTokenObtainSerializer(LifeTimeTokenSerializer, TokenObtainPairSerializer):
    pass


class LifeTimeTokenRefreshSerializer(LifeTimeTokenSerializer, TokenRefreshSerializer):
    pass


class RegisterUserByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, write_only=True)
    confirm_password = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        fields = [
            "email",
            "password",
            "confirm_password"
        ]

    def validate_password(self, password):
        if password != self.initial_data['confirm_password']:
            raise serializers.ValidationError(_("password mismatch."))
        return password

    def validate_email(self, email):
        if User.objects.filter(email=email, is_verified=True).exists():
            raise serializers.ValidationError(_('user with this email already exists.'))
        return email

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=password,
            )
        else:
            user.set_password(password)
            user.save()

        user.send_verification_email()

        return user


class RegisterUserByPhoneSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(validators=[
        RegexValidator(r'^9[0-3,9]\d{8}$', _('Enter a valid phone number.'), 'invalid'),
    ], )

    def create(self, validated_data):
        phone_number = validated_data['phone_number']

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            user = User.objects.create_user(
                phone_number=phone_number,
            )
        else:
            user.save()

        user.send_verification_sms()

        return user


class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return User.objects.get(email=data)


class VerifyUserSerializer(serializers.Serializer):
    rc = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True, is_verified=True).exists():
            raise serializers.ValidationError(
                {'email': 'invalid email address.'})
        return value

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        user.email_reset_password()


class SetPasswordSerializer(serializers.ModelSerializer):
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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('old_password', 'password', 'confirm_password')

    def validate_old_password(self, old_password):
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError(_('the old password you have entered is incorrect.'))
        return old_password

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': 'password mismatch'})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class SetPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField()

    def validate_phone_number(self, phone_number):
        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(_('user with this phone number is already exists.'))
        return phone_number


class VerifyPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField()
    verify_code = serializers.CharField()
