"""
Serializers for tenant models.
"""

from rest_framework import serializers
from .models import Tenant


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
        """Extract theme from metadata."""
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
