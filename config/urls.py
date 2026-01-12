"""
URL Configuration for multi-tenant API service.
All endpoints are versioned under /api/v1/
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin (can be disabled in production)
    path('admin/', admin.site.urls),
    
    # API v1 endpoints
    path('api/v1/', include('apps.authentication.urls')),
    path('api/v1/', include('apps.core.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
