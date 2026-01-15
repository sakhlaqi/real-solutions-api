"""
URL configuration for authentication endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    TenantTokenObtainPairView,
    APIClientTokenObtainView,
    APIClientRefreshTokenView,
    UserRegisterView,
    UserLogoutView,
    CurrentUserView,
)

app_name = 'authentication'

urlpatterns = [
    # User authentication endpoints
    path('auth/login/', TenantTokenObtainPairView.as_view(), name='login'),
    path('auth/register/', UserRegisterView.as_view(), name='register'),
    path('auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    
    # JWT Token endpoints (username/password)
    path('auth/token/', TenantTokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Client endpoints (client_id/client_secret)
    path('auth/api-client/token/', APIClientTokenObtainView.as_view(), name='api_client_token'),
    path('auth/api-client/token/refresh/', APIClientRefreshTokenView.as_view(), name='api_client_refresh'),
]
