"""
Serializers for tenant models.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Tenant, Theme, Template, TenantFeatureFlag, TenantRoute


class TenantSerializer(serializers.ModelSerializer):
    """
    Basic tenant serializer for public endpoints.
    """
    
    class Meta:
        model = Tenant
        fields = [
            'id',
            'name',
            'slug',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for tenant configuration including metadata.
    Used for both public and admin endpoints.
    """
    
    # Extract specific config from metadata
    branding = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()
    feature_flags = serializers.SerializerMethodField()
    routes = serializers.SerializerMethodField()
    page_config = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id',
            'name',
            'slug',
            'is_active',
            'branding',
            'theme',
            'feature_flags',
            'routes',
            'page_config',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_branding(self, obj):
        """Extract branding from metadata."""
        return obj.metadata.get('branding', {
            'name': obj.name,
            'tagline': '',
            'logo': {'light': '', 'dark': ''},
            'favicon': '',
        })
    
    def get_theme(self, obj):
        """
        Return theme metadata if theme is selected, otherwise legacy metadata theme.
        
        This maintains backward compatibility with existing tenants while
        supporting the new theme system.
        """
        # New theme system - return theme metadata
        theme_metadata = obj.get_theme_metadata()
        if theme_metadata:
            return {
                'metadata': theme_metadata,
                'json': obj.get_resolved_theme(),  # Full raw theme JSON
            }
        
        # Legacy fallback - return old metadata-based theme or None
        # Frontend should handle defaults when theme is None
        return obj.metadata.get('theme')
    
    def get_feature_flags(self, obj):
        """
        Extract feature flags from dedicated table or fall back to metadata.
        Returns a dict of {key: enabled} for easy frontend consumption.
        """
        # Try new table first
        flags_queryset = obj.feature_flags.all()
        if flags_queryset.exists():
            return {flag.key: flag.enabled for flag in flags_queryset}
        
        # Fall back to metadata for backward compatibility
        return obj.metadata.get('feature_flags', {})
    
    def get_routes(self, obj):
        """
        Extract dynamic routes from dedicated table or fall back to metadata.
        """
        # Try new table first
        routes_queryset = obj.routes_config.all()
        if routes_queryset.exists():
            return [
                {
                    'path': route.path,
                    'pagePath': route.page_path,
                    'title': route.title,
                    'exact': route.exact,
                    'protected': route.protected,
                    'layout': route.layout,
                    'order': route.order,
                }
                for route in routes_queryset
            ]
        
        # Fall back to metadata for backward compatibility
        # Return empty list if no routes configured - frontend should handle defaults
        return obj.metadata.get('routes', [])
    
    def get_page_config(self, obj):
        """
        Get page configuration from template system.
        
        Returns resolved template JSON (preset + overrides merged).
        If no template assigned, returns a minimal default page.
        """
        # Get pages from template system
        if obj.template:
            resolved_template = obj.template.get_resolved_template_json()
            return {
                'pages': resolved_template.get('pages', {}),
                'version': resolved_template.get('meta', {}).get('version', '1.0.0'),
                'template_id': str(obj.template.id),
                'template_name': obj.template.name,
                'template_category': obj.template.category,
            }
        
        # No template assigned - return None structure
        # Frontend should handle default pages/layouts
        return {
            'pages': None,
            'version': None,
            'template_id': None,
            'template_name': None,
        }
    
    def update(self, instance, validated_data):
        """
        Update tenant configuration.
        
        Handle nested metadata updates for branding, theme, etc.
        """
        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        
        # Get current metadata
        metadata = instance.metadata.copy()
        
        # Update metadata sections if provided in request data
        request_data = self.context.get('request').data if self.context.get('request') else {}
        
        if 'branding' in request_data:
            metadata['branding'] = request_data['branding']
        
        if 'theme' in request_data:
            metadata['theme'] = request_data['theme']
        
        if 'feature_flags' in request_data:
            metadata['feature_flags'] = request_data['feature_flags']
        
        if 'routes' in request_data:
            metadata['routes'] = request_data['routes']
        
        if 'page_config' in request_data:
            metadata['page_config'] = request_data['page_config']
        
        instance.metadata = metadata
        instance.save()
        
        return instance


class ThemeSerializer(serializers.ModelSerializer):
    """
    Serializer for Theme model with read-only protection for presets.
    Supports theme inheritance - custom themes can extend presets.
    """
    
    # Read-only fields
    is_read_only = serializers.SerializerMethodField()
    supported_modes = serializers.SerializerMethodField()
    resolved_theme_json = serializers.SerializerMethodField()
    inheritance_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Theme
        fields = [
            'id',
            'name',
            'version',
            'is_preset',
            'is_read_only',
            'theme_json',
            'base_preset',
            'token_overrides',
            'resolved_theme_json',
            'inheritance_info',
            'tenant',
            'created_by',
            'created_at',
            'updated_at',
            'supported_modes',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'is_read_only',
            'supported_modes',
            'resolved_theme_json',
            'inheritance_info',
        ]
    
    def get_is_read_only(self, obj):
        """Presets are read-only."""
        return obj.is_read_only()
    
    def get_supported_modes(self, obj):
        """Get list of supported mode names from resolved theme."""
        resolved = obj.get_resolved_theme_json()
        modes = resolved.get('modes', {})
        return list(modes.keys()) if modes else []
    
    def get_resolved_theme_json(self, obj):
        """Get complete theme JSON (merged if inherited)."""
        return obj.get_resolved_theme_json()
    
    def get_inheritance_info(self, obj):
        """Get inheritance information."""
        return obj.get_inheritance_info()
    
    def validate(self, attrs):
        """Validate theme data before save."""
        # Prevent modification of presets
        if self.instance and self.instance.is_preset:
            raise serializers.ValidationError(
                "Cannot modify preset themes. Preset themes are read-only."
            )
        
        # Ensure name and version match theme_json
        theme_json = attrs.get('theme_json', self.instance.theme_json if self.instance else None)
        if theme_json:
            meta = theme_json.get('meta', {})
            
            # Sync name
            if 'name' in attrs and attrs['name'] != meta.get('name'):
                raise serializers.ValidationError(
                    f"Theme name must match theme_json.meta.name ('{meta.get('name')}')"
                )
            
            # Sync version
            if 'version' in attrs and attrs['version'] != meta.get('version'):
                raise serializers.ValidationError(
                    f"Theme version must match theme_json.meta.version ('{meta.get('version')}')"
                )
            
            # Auto-sync if not explicitly set
            if 'name' not in attrs and meta.get('name'):
                attrs['name'] = meta['name']
            if 'version' not in attrs and meta.get('version'):
                attrs['version'] = meta['version']
        
        return attrs
    
    def create(self, validated_data):
        """Create new theme (not allowed for presets)."""
        if validated_data.get('is_preset', False):
            raise serializers.ValidationError(
                "Cannot create preset themes via API. Use management command 'seed_theme_presets'."
            )
        
        # Set tenant from request context if not provided
        if 'tenant' not in validated_data and self.context.get('request'):
            # In a real implementation, you'd get tenant from request user/JWT
            # For now, raise error if tenant not provided
            raise serializers.ValidationError("Tenant is required for custom themes")
        
        # Set created_by from request user
        if 'created_by' not in validated_data and self.context.get('request'):
            validated_data['created_by'] = self.context['request'].user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update theme (not allowed for presets)."""
        if instance.is_preset:
            raise serializers.ValidationError(
                "Cannot update preset themes. Preset themes are read-only."
            )
        
        # Prevent changing is_preset flag
        if 'is_preset' in validated_data and validated_data['is_preset'] != instance.is_preset:
            raise serializers.ValidationError("Cannot change is_preset flag")
        
        return super().update(instance, validated_data)


class ThemeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing themes (without full theme_json).
    """
    
    is_read_only = serializers.SerializerMethodField()
    supported_modes = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Theme
        fields = [
            'id',
            'name',
            'version',
            'is_preset',
            'is_read_only',
            'category',
            'tags',
            'supported_modes',
            'created_at',
            'updated_at',
        ]
    
    def get_is_read_only(self, obj):
        return obj.is_read_only()
    
    def get_supported_modes(self, obj):
        modes = obj.theme_json.get('modes', {})
        return list(modes.keys()) if modes else []
    
    def get_category(self, obj):
        return obj.theme_json.get('meta', {}).get('category')
    
    def get_tags(self, obj):
        return obj.theme_json.get('meta', {}).get('tags', [])


# ============================================================================
# Template Serializers
# ============================================================================

class TemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for Template model with read-only protection for presets.
    Supports template inheritance - custom templates can extend presets.
    """
    
    # Read-only fields
    is_read_only = serializers.SerializerMethodField()
    resolved_template_json = serializers.SerializerMethodField()
    inheritance_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id',
            'name',
            'version',
            'is_preset',
            'is_read_only',
            'category',
            'tier',
            'description',
            'preview_image',
            'tags',
            'template_json',
            'base_preset',
            'template_overrides',
            'resolved_template_json',
            'inheritance_info',
            'tenant',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'is_read_only',
            'resolved_template_json',
            'inheritance_info',
        ]
    
    def get_is_read_only(self, obj):
        """Presets are read-only."""
        return obj.is_read_only()
    
    def get_resolved_template_json(self, obj):
        """Get complete template JSON (merged if inherited)."""
        return obj.get_resolved_template_json()
    
    def get_inheritance_info(self, obj):
        """Get inheritance information."""
        return obj.get_inheritance_info()
    
    def validate(self, attrs):
        """Validate template data before save."""
        # Prevent modification of presets
        if self.instance and self.instance.is_preset:
            raise serializers.ValidationError(
                "Cannot modify preset templates. Preset templates are read-only."
            )
        
        # Ensure name, version, category, tier match template_json meta
        template_json = attrs.get('template_json', self.instance.template_json if self.instance else None)
        if template_json and 'meta' in template_json:
            meta = template_json['meta']
            
            name = attrs.get('name', self.instance.name if self.instance else None)
            if name and meta.get('name') != name:
                raise serializers.ValidationError({
                    'template_json': f"template_json.meta.name must match template name: '{name}'"
                })
            
            version = attrs.get('version', self.instance.version if self.instance else '1.0.0')
            if meta.get('version') != version:
                raise serializers.ValidationError({
                    'template_json': f"template_json.meta.version must match template version: '{version}'"
                })
            
            category = attrs.get('category', self.instance.category if self.instance else 'custom')
            if meta.get('category') != category:
                raise serializers.ValidationError({
                    'template_json': f"template_json.meta.category must match template category: '{category}'"
                })
            
            tier = attrs.get('tier', self.instance.tier if self.instance else 'free')
            if meta.get('tier') != tier:
                raise serializers.ValidationError({
                    'template_json': f"template_json.meta.tier must match template tier: '{tier}'"
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create new template (not allowed for presets)."""
        if validated_data.get('is_preset', False):
            raise serializers.ValidationError(
                "Cannot create preset templates via API. Use management commands."
            )
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update template (not allowed for presets or changing preset flag)."""
        # Prevent changing is_preset flag
        if 'is_preset' in validated_data and validated_data['is_preset'] != instance.is_preset:
            raise serializers.ValidationError("Cannot change is_preset flag")
        
        return super().update(instance, validated_data)


class TemplateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing templates (without full template_json).
    """
    
    is_read_only = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id',
            'name',
            'version',
            'is_preset',
            'is_read_only',
            'category',
            'tier',
            'description',
            'preview_image',
            'tags',
            'created_at',
            'updated_at',
        ]
    
    def get_is_read_only(self, obj):
        return obj.is_read_only()


class TenantFeatureFlagSerializer(serializers.ModelSerializer):
    """
    Serializer for TenantFeatureFlag CRUD operations.
    """
    
    class Meta:
        model = TenantFeatureFlag
        fields = [
            'id',
            'tenant',
            'key',
            'enabled',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate that key doesn't already exist for this tenant."""
        tenant = attrs.get('tenant')
        key = attrs.get('key')
        
        # For updates, exclude current instance
        if self.instance:
            existing = TenantFeatureFlag.objects.filter(
                tenant=tenant, key=key
            ).exclude(id=self.instance.id)
        else:
            existing = TenantFeatureFlag.objects.filter(tenant=tenant, key=key)
        
        if existing.exists():
            raise serializers.ValidationError(
                f"Feature flag '{key}' already exists for this tenant"
            )
        
        return attrs


class TenantRouteSerializer(serializers.ModelSerializer):
    """
    Serializer for TenantRoute CRUD operations.
    """
    
    class Meta:
        model = TenantRoute
        fields = [
            'id',
            'tenant',
            'path',
            'page_path',
            'title',
            'exact',
            'protected',
            'layout',
            'order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate that path doesn't already exist for this tenant."""
        tenant = attrs.get('tenant')
        path = attrs.get('path')
        
        # For updates, exclude current instance
        if self.instance:
            existing = TenantRoute.objects.filter(
                tenant=tenant, path=path
            ).exclude(id=self.instance.id)
        else:
            existing = TenantRoute.objects.filter(tenant=tenant, path=path)
        
        if existing.exists():
            raise serializers.ValidationError(
                f"Route '{path}' already exists for this tenant"
            )
        
        return attrs



# TenantPageConfigSerializer removed - replaced by Template system


