"""Auth API: registration, login, logout, profile, JWT (obtain + refresh)."""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from . import views
from .throttling import AuthRateThrottle

app_name = 'accounts'


# JWT: accept "email" (same as login API) and apply auth rate limit
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = self.fields.pop('username')


class ThrottledTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = [AuthRateThrottle]

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.MeView.as_view(), name='me'),
    path('jwt/token/', ThrottledTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
