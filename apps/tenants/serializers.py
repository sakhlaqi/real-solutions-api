"""
Serializers for tenant models.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Tenant, Theme


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
    layout_preferences = serializers.SerializerMethodField()
    landing_page_sections = serializers.SerializerMethodField()
    routes = serializers.SerializerMethodField()
    
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
            'layout_preferences',
            'landing_page_sections',
            'routes',
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
        
        # Legacy fallback - return old metadata-based theme
        default_theme = {
            'colors': {
                'primary': '#0066cc',
                'secondary': '#ff6600',
                'accent': '#00cc99',
                'background': '#ffffff',
                'surface': '#f8f9fa',
                'text': {
                    'primary': '#212529',
                    'secondary': '#6c757d',
                    'inverse': '#ffffff'
                },
                'error': '#dc3545',
                'success': '#28a745',
                'warning': '#ffc107'
            },
            'fonts': {
                'primary': 'Inter, sans-serif',
                'secondary': 'Georgia, serif',
                'sizes': {
                    'xs': '0.75rem',
                    'sm': '0.875rem',
                    'base': '1rem',
                    'lg': '1.125rem',
                    'xl': '1.25rem',
                    '2xl': '1.5rem',
                    '3xl': '1.875rem'
                }
            },
            'spacing': {
                'xs': '0.25rem',
                'sm': '0.5rem',
                'md': '1rem',
                'lg': '1.5rem',
                'xl': '2rem',
                '2xl': '3rem'
            },
            'borderRadius': {
                'sm': '0.25rem',
                'md': '0.5rem',
                'lg': '1rem',
                'full': '9999px'
            },
            'shadows': {
                'sm': '0 1px 2px rgba(0,0,0,0.05)',
                'md': '0 4px 6px rgba(0,0,0,0.1)',
                'lg': '0 10px 15px rgba(0,0,0,0.1)'
            }
        }
        return obj.metadata.get('theme', default_theme)
    
    def get_feature_flags(self, obj):
        """Extract feature flags from metadata."""
        return obj.metadata.get('feature_flags', {})
    
    def get_layout_preferences(self, obj):
        """Extract layout preferences from metadata."""
        return obj.metadata.get('layout_preferences', {
            'headerStyle': 'default',
            'footerStyle': 'default',
        })
    
    def get_landing_page_sections(self, obj):
        """Extract landing page sections from metadata."""
        return obj.metadata.get('landing_page_sections', [])
    
    def get_routes(self, obj):
        """Extract dynamic routes configuration from metadata."""
        default_routes = [
            {
                'path': '/',
                'pagePath': '/',
                'title': 'Home',
                'protected': False,
                'layout': 'main',
                'order': 0
            },
            {
                'path': '/login',
                'pagePath': '/login',
                'title': 'Login',
                'protected': False,
                'layout': 'none',
                'order': 1
            },
            {
                'path': '/admin',
                'pagePath': '/dashboard',
                'title': 'Dashboard',
                'protected': True,
                'layout': 'admin',
                'order': 2
            }
        ]
        return obj.metadata.get('routes', default_routes)
    
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
        
        if 'layout_preferences' in request_data:
            metadata['layout_preferences'] = request_data['layout_preferences']
        
        if 'landing_page_sections' in request_data:
            metadata['landing_page_sections'] = request_data['landing_page_sections']
        
        if 'routes' in request_data:
            metadata['routes'] = request_data['routes']
        
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

