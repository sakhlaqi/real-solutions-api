"""
URL configuration for authentication endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import TenantTokenObtainPairView

app_name = 'authentication'

urlpatterns = [
    # JWT Token endpoints
    path('auth/token/', TenantTokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
