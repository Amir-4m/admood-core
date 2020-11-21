from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())

        return data


class MyTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
        return data


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
            raise serializers.ValidationError("password mismatch.")
        return password

    def validate_email(self, email):
        if User.objects.filter(email=email, is_verified=True).exists():
            raise serializers.ValidationError('user with this email already exists.')
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
        if self.instance.check_password(old_password):
            return old_password
        raise serializers.ValidationError({'old_password': 'The old password you have entered is incorrect.'})

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': 'password mismatch'})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

