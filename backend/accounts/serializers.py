"""
Serializers for registration and login.
Structured for React frontend consumption.
High security: password validation via AUTH_PASSWORD_VALIDATORS.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Address

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    """Address for nesting in order payloads and user profile."""

    class Meta:
        model = Address
        fields = (
            'id', 'label', 'full_name', 'phone', 'line1', 'line2',
            'city', 'state_region', 'postal_code', 'country', 'is_default',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Registration: email, password, full_name (required); phone, preferred_lang optional.
    Passwords validated with AUTH_PASSWORD_VALIDATORS (min length 10, complexity).
    """
    password = serializers.CharField(write_only=True, min_length=10, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'full_name',
            'phone',
            'preferred_lang',
            'role',
        )
        read_only_fields = ('id', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True},
        }

    def validate_password(self, value):
        try:
            validate_password(value, self.instance)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.setdefault('role', 'customer')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Read/write user profile (no password). Used for GET profile and PATCH updates.
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'full_name',
            'phone',
            'preferred_lang',
            'role',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'email', 'role', 'is_active', 'created_at', 'updated_at')


class UserLoginSerializer(serializers.Serializer):
    """
    Login: email + password. Returns user + token when used with auth view.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
