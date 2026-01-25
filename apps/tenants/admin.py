"""
Django admin configuration for Tenant models.
"""

from django.contrib import admin
from .models import Tenant, Theme


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""
    
    list_display = ['name', 'slug', 'id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Identification', {
            'fields': ('id',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
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

