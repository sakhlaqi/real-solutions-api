"""
API views for tenant endpoints.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.authentication.permissions import IsTenantUser
from .models import Tenant, Theme
from .serializers import (
    TenantSerializer, 
    TenantConfigSerializer,
    ThemeSerializer,
    ThemeListSerializer,
)


class TenantBySlugView(APIView):
    """
    Public endpoint to get tenant by slug.
    No authentication required.
    
    GET /tenants/{slug}/
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Get tenant by slug."""
        tenant = get_object_or_404(Tenant, slug=slug, is_active=True)
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)


class TenantConfigView(APIView):
    """
    Tenant configuration endpoints.
    
    GET /tenants/{id}/config/ - Public, no auth required
    PATCH /tenants/{id}/config/ - Protected, requires admin access
    """
    
    def get_authenticators(self):
        """
        GET has no auth, PATCH requires JWT authentication.
        """
        if self.request.method == 'GET':
            return []
        return super().get_authenticators()
    
    def get_permissions(self):
        """
        GET is public, PATCH requires authentication.
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsTenantUser()]
    
    def get(self, request, pk):
        """
        Get tenant configuration (public endpoint).
        
        GET /tenants/{id}/config/
        """
        tenant = get_object_or_404(Tenant, pk=pk, is_active=True)
        serializer = TenantConfigSerializer(tenant)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        """
        Update tenant configuration (admin only).
        
        PATCH /tenants/{id}/config/
        """
        # Ensure user can only update their own tenant
        if str(request.tenant.id) != str(pk):
            return Response(
                {'error': 'You can only update your own tenant configuration'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tenant = get_object_or_404(Tenant, pk=pk, is_active=True)
        serializer = TenantConfigSerializer(
            tenant,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantConfigBySlugView(APIView):
    """
    Public endpoint to get tenant configuration by slug.
    No authentication required.
    
    GET /tenants/{slug}/config/
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Get tenant configuration by slug."""
        tenant = get_object_or_404(Tenant, slug=slug, is_active=True)
        serializer = TenantConfigSerializer(tenant)
        return Response(serializer.data)


class TenantViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing tenants.
    Requires authentication and tenant user permission.
    
    Endpoints:
    - GET /tenants/ - List all tenants (superuser only)
    - POST /tenants/ - Create tenant (superuser only)
    - GET /tenants/{id}/ - Get tenant details
    - PUT /tenants/{id}/ - Update tenant
    - PATCH /tenants/{id}/ - Partial update tenant
    - DELETE /tenants/{id}/ - Delete tenant (superuser only)
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Regular users can only see their own tenant.
        Superusers can see all tenants.
        """
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        
        # Regular users only see their tenant
        if hasattr(self.request, 'tenant'):
            return Tenant.objects.filter(id=self.request.tenant.id)
        
        return Tenant.objects.none()


class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Theme model - read-only access.
    
    Public endpoints (no authentication required):
    - GET /themes/ - List all preset themes (lightweight)
    - GET /themes/{id}/ - Get full theme by ID (including theme_json)
    
    Presets are always available to all tenants.
    Custom themes are only visible to their owning tenant.
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Return presets for unauthenticated users.
        Return presets + tenant's custom themes for authenticated users.
        """
        # Get all presets (always visible)
        queryset = Theme.objects.filter(is_preset=True)
        
        # Add tenant's custom themes if authenticated
        if self.request.user.is_authenticated and hasattr(self.request, 'tenant'):
            tenant_themes = Theme.objects.filter(tenant=self.request.tenant)
            queryset = queryset | tenant_themes
        
        return queryset.order_by('-is_preset', 'name')
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list, full serializer for detail.
        """
        if self.action == 'list':
            return ThemeListSerializer
        return ThemeSerializer
    
    @action(detail=False, methods=['get'])
    def presets(self, request):
        """
        GET /themes/presets/
        
        Get all preset themes (lightweight list).
        Convenience endpoint for fetching only official presets.
        """
        presets = Theme.get_presets()
        serializer = ThemeListSerializer(presets, many=True)
        return Response(serializer.data)
