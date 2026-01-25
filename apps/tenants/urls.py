"""
URL configuration for tenant endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TenantViewSet,
    TenantBySlugView,
    TenantConfigView,
    TenantConfigBySlugView,
    ThemeViewSet,
)

app_name = 'tenants'

# Router for standard CRUD operations
router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'themes', ThemeViewSet, basename='theme')

urlpatterns = [
    # Public endpoints (no auth required)
    path('tenants/<slug:slug>/', TenantBySlugView.as_view(), name='tenant-by-slug'),
    path('tenants/<slug:slug>/config/', TenantConfigBySlugView.as_view(), name='tenant-config-by-slug'),
    
    # Tenant configuration endpoints
    path('tenants/<uuid:pk>/config/', TenantConfigView.as_view(), name='tenant-config'),
    
    # Standard CRUD endpoints (protected)
    path('', include(router.urls)),
]
