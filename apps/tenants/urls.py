"""
URL configuration for tenant endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    TenantViewSet,
    TenantBySlugView,
    TenantConfigView,
    TenantConfigBySlugView,
    ThemeViewSet,
    TenantFeatureFlagViewSet,
    TenantRouteViewSet,
    TenantPageConfigViewSet,
)

app_name = 'tenants'

# Router for standard CRUD operations
router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'themes', ThemeViewSet, basename='theme')

# Nested routers for tenant-specific resources
tenants_router = routers.NestedDefaultRouter(router, r'tenants', lookup='tenant')
tenants_router.register(r'feature-flags', TenantFeatureFlagViewSet, basename='tenant-feature-flags')
tenants_router.register(r'routes', TenantRouteViewSet, basename='tenant-routes')
tenants_router.register(r'page-config', TenantPageConfigViewSet, basename='tenant-page-config')

urlpatterns = [
    # Public endpoints (no auth required)
    path('tenants/<slug:slug>/', TenantBySlugView.as_view(), name='tenant-by-slug'),
    path('tenants/<slug:slug>/config/', TenantConfigBySlugView.as_view(), name='tenant-config-by-slug'),
    
    # Tenant configuration endpoints
    path('tenants/<uuid:pk>/config/', TenantConfigView.as_view(), name='tenant-config'),
    
    # Standard CRUD endpoints (protected)
    path('', include(router.urls)),
    
    # Nested CRUD endpoints for tenant resources
    path('', include(tenants_router.urls)),
]
