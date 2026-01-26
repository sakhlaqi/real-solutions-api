"""
API views for tenant endpoints.
"""

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.authentication.permissions import IsTenantUser
from .models import Tenant, Theme, TenantFeatureFlag, TenantPageConfig, TenantRoute
from .serializers import (
    TenantSerializer, 
    TenantConfigSerializer,
    ThemeSerializer,
    ThemeListSerializer,
    TenantFeatureFlagSerializer,
    TenantRouteSerializer,
    TenantPageConfigSerializer,
)
from datetime import datetime


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


class ThemeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Theme model.
    
    Public endpoints (no authentication required):
    - GET /themes/ - List all preset themes (lightweight)
    - GET /themes/{id}/ - Get full theme by ID (including theme_json)
    
    Authenticated endpoints (require tenant authentication):
    - POST /themes/ - Create custom theme
    - PUT /themes/{id}/ - Update custom theme
    - PATCH /themes/{id}/ - Partially update custom theme
    - DELETE /themes/{id}/ - Delete custom theme
    
    Presets are always available to all tenants.
    Custom themes are only visible to their owning tenant.
    Custom themes can extend presets using base_preset and token_overrides.
    """
    
    def get_permissions(self):
        """
        List and retrieve are public.
        Create, update, delete require authentication.
        """
        if self.action in ['list', 'retrieve', 'presets']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
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
    
    def perform_create(self, serializer):
        """
        Create custom theme for current tenant.
        Auto-set tenant and created_by from request.
        """
        # Prevent creating presets via API
        if serializer.validated_data.get('is_preset', False):
            raise serializers.ValidationError(
                "Cannot create preset themes via API. Use management command 'seed_theme_presets'."
            )
        
        # Set tenant from request
        if not hasattr(self.request, 'tenant'):
            raise serializers.ValidationError("Tenant context required")
        
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """
        Update custom theme.
        Prevent updating presets and changing ownership.
        """
        instance = self.get_object()
        
        if instance.is_preset:
            raise serializers.ValidationError(
                "Cannot update preset themes. Preset themes are read-only."
            )
        
        # Prevent changing tenant
        if 'tenant' in serializer.validated_data:
            if serializer.validated_data['tenant'] != instance.tenant:
                raise serializers.ValidationError("Cannot change theme tenant")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete custom theme.
        Prevent deleting presets.
        """
        if instance.is_preset:
            raise serializers.ValidationError(
                "Cannot delete preset themes."
            )
        
        # Check if any tenant is using this theme
        if instance.tenants_using.exists():
            raise serializers.ValidationError(
                f"Cannot delete theme. {instance.tenants_using.count()} tenant(s) are using it."
            )
        
        instance.delete()
    
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
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """
        POST /themes/{id}/clone/
        
        Clone a theme (preset or custom) to create a new custom theme.
        Optionally provide token_overrides to customize the clone.
        
        Request body:
        {
            "name": "My Custom Theme",
            "version": "1.0.0",
            "token_overrides": {
                "colors": {"primary": "#ff0000"}
            }
        }
        """
        source_theme = self.get_object()
        
        name = request.data.get('name')
        version = request.data.get('version', '1.0.0')
        token_overrides = request.data.get('token_overrides', {})
        
        if not name:
            raise serializers.ValidationError("Name is required")
        
        # Check if tenant already has a theme with this name
        if Theme.objects.filter(
            tenant=self.request.tenant,
            name=name
        ).exists():
            raise serializers.ValidationError(
                f"Theme with name '{name}' already exists for this tenant"
            )
        
        # Create new theme extending the source
        if source_theme.is_preset:
            # Clone from preset - use inheritance
            new_theme = Theme.objects.create(
                name=name,
                version=version,
                is_preset=False,
                tenant=self.request.tenant,
                created_by=self.request.user,
                base_preset=source_theme,
                token_overrides=token_overrides,
                theme_json={
                    'meta': {
                        'id': name.lower().replace(' ', '-'),
                        'name': name,
                        'version': version,
                        'category': 'custom',
                        'description': f"Based on {source_theme.name}"
                    }
                }
            )
        else:
            # Clone from custom theme - create standalone copy
            from .utils import deep_merge_tokens
            
            source_resolved = source_theme.get_resolved_theme_json()
            merged_tokens = deep_merge_tokens(
                source_resolved.get('tokens', {}),
                token_overrides
            )
            
            new_theme = Theme.objects.create(
                name=name,
                version=version,
                is_preset=False,
                tenant=self.request.tenant,
                created_by=self.request.user,
                theme_json={
                    'meta': {
                        'id': name.lower().replace(' ', '-'),
                        'name': name,
                        'version': version,
                        'category': 'custom',
                        'description': f"Based on {source_theme.name}"
                    },
                    'tokens': merged_tokens,
                    'modes': source_resolved.get('modes', {})
                }
            )
        
        serializer = ThemeSerializer(new_theme)
        return Response(serializer.data, status=201)


class TenantFeatureFlagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TenantFeatureFlag CRUD operations.
    
    GET    /tenants/{tenant_id}/feature-flags/        - List all feature flags
    POST   /tenants/{tenant_id}/feature-flags/        - Create new feature flag
    GET    /tenants/{tenant_id}/feature-flags/{id}/   - Get specific feature flag
    PATCH  /tenants/{tenant_id}/feature-flags/{id}/   - Update feature flag
    PUT    /tenants/{tenant_id}/feature-flags/{id}/   - Replace feature flag
    DELETE /tenants/{tenant_id}/feature-flags/{id}/   - Delete feature flag
    """
    serializer_class = TenantFeatureFlagSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    def get_queryset(self):
        """Filter feature flags by tenant from URL."""
        tenant_id = self.kwargs.get('tenant_pk')
        return TenantFeatureFlag.objects.filter(tenant_id=tenant_id)
    
    def perform_create(self, serializer):
        """Ensure tenant is set from URL."""
        tenant_id = self.kwargs.get('tenant_pk')
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        
        # Ensure user can only create for their own tenant
        if str(self.request.tenant.id) != str(tenant_id):
            raise serializers.ValidationError(
                "You can only create feature flags for your own tenant"
            )
        
        serializer.save(tenant=tenant)


class TenantRouteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TenantRoute CRUD operations.
    
    GET    /tenants/{tenant_id}/routes/        - List all routes
    POST   /tenants/{tenant_id}/routes/        - Create new route
    GET    /tenants/{tenant_id}/routes/{id}/   - Get specific route
    PATCH  /tenants/{tenant_id}/routes/{id}/   - Update route
    PUT    /tenants/{tenant_id}/routes/{id}/   - Replace route
    DELETE /tenants/{tenant_id}/routes/{id}/   - Delete route
    """
    serializer_class = TenantRouteSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    def get_queryset(self):
        """Filter routes by tenant from URL."""
        tenant_id = self.kwargs.get('tenant_pk')
        return TenantRoute.objects.filter(tenant_id=tenant_id).order_by('order', 'path')
    
    def perform_create(self, serializer):
        """Ensure tenant is set from URL."""
        tenant_id = self.kwargs.get('tenant_pk')
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        
        # Ensure user can only create for their own tenant
        if str(self.request.tenant.id) != str(tenant_id):
            raise serializers.ValidationError(
                "You can only create routes for your own tenant"
            )
        
        serializer.save(tenant=tenant)


class TenantPageConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TenantPageConfig CRUD operations.
    
    Note: This is a singleton resource per tenant (OneToOne relationship).
    
    GET    /tenants/{tenant_id}/page-config/   - Get page configuration
    POST   /tenants/{tenant_id}/page-config/   - Create page configuration
    PATCH  /tenants/{tenant_id}/page-config/   - Update page configuration
    PUT    /tenants/{tenant_id}/page-config/   - Replace page configuration
    DELETE /tenants/{tenant_id}/page-config/   - Delete page configuration
    """
    serializer_class = TenantPageConfigSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']
    
    def get_queryset(self):
        """Filter page config by tenant from URL."""
        tenant_id = self.kwargs.get('tenant_pk')
        return TenantPageConfig.objects.filter(tenant_id=tenant_id)
    
    def get_object(self):
        """Get or create the page config for this tenant."""
        tenant_id = self.kwargs.get('tenant_pk')
        
        # Ensure user can only access their own tenant
        if str(self.request.tenant.id) != str(tenant_id):
            raise serializers.ValidationError(
                "You can only access your own tenant's page configuration"
            )
        
        # For OneToOne, we want to get the single instance or 404
        return get_object_or_404(TenantPageConfig, tenant_id=tenant_id)
    
    def list(self, request, *args, **kwargs):
        """Return single object instead of list for OneToOne relationship."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            # Return empty if doesn't exist
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def perform_create(self, serializer):
        """Ensure tenant is set from URL and only one config per tenant."""
        tenant_id = self.kwargs.get('tenant_pk')
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        
        # Ensure user can only create for their own tenant
        if str(self.request.tenant.id) != str(tenant_id):
            raise serializers.ValidationError(
                "You can only create page configuration for your own tenant"
            )
        
        # Check if config already exists
        if TenantPageConfig.objects.filter(tenant=tenant).exists():
            raise serializers.ValidationError(
                "Page configuration already exists for this tenant. Use PATCH to update."
            )
        
        serializer.save(tenant=tenant)
