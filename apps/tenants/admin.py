"""
Django admin configuration for Tenant models.
"""

from django.contrib import admin
from .models import Tenant, Theme, TenantFeatureFlag, TenantPageConfig, TenantRoute


class TenantFeatureFlagInline(admin.TabularInline):
    """Inline admin for tenant feature flags."""
    model = TenantFeatureFlag
    extra = 0
    fields = ['key', 'enabled', 'description']
    ordering = ['key']


class TenantRouteInline(admin.TabularInline):
    """Inline admin for tenant routes."""
    model = TenantRoute
    extra = 0
    fields = ['path', 'page_path', 'title', 'exact', 'protected', 'layout', 'order']
    ordering = ['order', 'path']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""
    
    list_display = ['name', 'slug', 'id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [TenantFeatureFlagInline, TenantRouteInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Theme', {
            'fields': ('theme', 'theme_modes')
        }),
        ('Identification', {
            'fields': ('id',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
            'description': 'Legacy metadata field - new configs should use dedicated tables'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Admin interface for Theme model."""
    
    list_display = ['name', 'version', 'is_preset', 'tenant', 'created_at']
    list_filter = ['is_preset', 'created_at']
    search_fields = ['name', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_read_only']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'version', 'is_preset')
        }),
        ('Identification', {
            'fields': ('id',)
        }),
        ('Ownership', {
            'fields': ('tenant', 'created_by')
        }),
        ('Theme Data', {
            'fields': ('theme_json',)
        }),
        ('Metadata', {
            'fields': ('is_read_only',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_read_only(self, obj):
        """Display read-only status."""
        return obj.is_read_only()
    is_read_only.boolean = True
    is_read_only.short_description = 'Read Only'
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of preset themes."""
        if obj and obj.is_preset:
            return False
        return super().has_delete_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of preset themes."""
        if obj and obj.is_preset:
            return False
        return super().has_change_permission(request, obj)


@admin.register(TenantFeatureFlag)
class TenantFeatureFlagAdmin(admin.ModelAdmin):
    """Admin interface for TenantFeatureFlag model."""
    
    list_display = ['tenant', 'key', 'enabled', 'created_at']
    list_filter = ['enabled', 'created_at']
    search_fields = ['tenant__name', 'tenant__slug', 'key', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Feature Flag', {
            'fields': ('key', 'enabled', 'description')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TenantPageConfig)
class TenantPageConfigAdmin(admin.ModelAdmin):
    """Admin interface for TenantPageConfig model."""
    
    list_display = ['tenant', 'version', 'page_count', 'created_at', 'updated_at']
    list_filter = ['version', 'created_at']
    search_fields = ['tenant__name', 'tenant__slug']
    readonly_fields = ['id', 'created_at', 'updated_at', 'page_count']
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Configuration', {
            'fields': ('version', 'pages', 'page_count')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def page_count(self, obj):
        """Display number of configured pages."""
        return len(obj.pages) if obj.pages else 0
    page_count.short_description = 'Page Count'


@admin.register(TenantRoute)
class TenantRouteAdmin(admin.ModelAdmin):
    """Admin interface for TenantRoute model."""
    
    list_display = ['tenant', 'path', 'page_path', 'title', 'protected', 'layout', 'order']
    list_filter = ['tenant', 'protected', 'layout']
    search_fields = ['tenant__name', 'tenant__slug', 'path', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['tenant', 'order', 'path']
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Route Configuration', {
            'fields': ('path', 'page_path', 'title', 'exact')
        }),
        ('Settings', {
            'fields': ('protected', 'layout', 'order')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

