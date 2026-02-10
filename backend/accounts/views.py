"""
Auth views: Registration, Login, Logout, Profile.
Uses Token authentication; thin views with logic in serializers.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer
from .models import User
from .throttling import AuthRateThrottle


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


class LoginView(APIView):
    """POST /api/auth/login/ — Login with email/password. Returns user + token. Rate limited."""
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'detail': 'Account is disabled.'}, status=status.HTTP_403_FORBIDDEN)
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
