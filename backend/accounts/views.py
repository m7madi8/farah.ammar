"""
Auth views: Registration, Login, Logout, Profile.
Uses Token authentication; thin views with logic in serializers.
High security: login lockout after failed attempts, security logging.
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings

from .serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer
from .models import User
from .throttling import AuthRateThrottle

logger = logging.getLogger('security')

LOCKOUT_CACHE_PREFIX = 'login_fail:'
MAX_ATTEMPTS = getattr(settings, 'LOGIN_FAILED_MAX_ATTEMPTS', 5)
LOCKOUT_DURATION = getattr(settings, 'LOGIN_LOCKOUT_DURATION', 900)


class RegisterView(APIView):
    """POST /api/auth/register/ — Register a new user. Returns user + auth token. Rate limited."""
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
        }, status=status.HTTP_201_CREATED)


def _login_lockout_key(identifier: str) -> str:
    return f"{LOCKOUT_CACHE_PREFIX}{identifier}"

def _get_client_identifier(request) -> str:
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


class LoginView(APIView):
    """POST /api/auth/login/ — Login with email/password. Rate limited + lockout after failed attempts."""
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']
        client_id = _get_client_identifier(request)

        # Lockout by email + IP to avoid blocking whole IP for one user
        lockout_key = _login_lockout_key(f"{email}:{client_id}")
        attempts = cache.get(lockout_key, 0)
        if attempts >= MAX_ATTEMPTS:
            logger.warning("Login locked out: email=%s, ip=%s", email, client_id)
            return Response(
                {'detail': 'Too many failed attempts. Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            new_count = attempts + 1
            cache.set(lockout_key, new_count, LOCKOUT_DURATION)
            logger.warning("Login failed: email=%s, ip=%s, attempt=%s", email, client_id, new_count)
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'detail': 'Account is disabled.'}, status=status.HTTP_403_FORBIDDEN)

        cache.delete(lockout_key)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
        })


class LogoutView(APIView):
    """POST /api/auth/logout/ — Invalidate current token (logout)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    """GET /api/auth/me/ — Get profile. PATCH /api/auth/me/ — Update profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
