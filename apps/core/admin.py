"""
Django admin configuration for core models.
"""

from django.contrib import admin
from .models import Project, Task, Document


class TenantAdminMixin:
    """
    Mixin for admin classes to filter by tenant.
    """
    
    def get_queryset(self, request):
        """Filter queryset by tenant for non-superusers."""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        # If user has tenant context, filter by it
        if hasattr(request, 'tenant'):
            return qs.filter(tenant=request.tenant)
        
        return qs
    
    def save_model(self, request, obj, form, change):
        """Automatically set tenant when creating objects."""
        if not change and hasattr(request, 'tenant'):
            obj.tenant = request.tenant
        super().save_model(request, obj, form, change)


@admin.register(Project)
class ProjectAdmin(TenantAdminMixin, admin.ModelAdmin):
    """Admin interface for Project model."""
    
    list_display = ['name', 'tenant', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'tenant']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'name', 'description', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Task)
class TaskAdmin(TenantAdminMixin, admin.ModelAdmin):
    """Admin interface for Task model."""
    
    list_display = ['title', 'project', 'tenant', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority', 'created_at', 'tenant']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'project', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(TenantAdminMixin, admin.ModelAdmin):
    """Admin interface for Document model."""
    
    list_display = ['name', 'tenant', 'project', 'content_type', 'file_size', 'created_at']
    list_filter = ['content_type', 'created_at', 'tenant']
    search_fields = ['name', 'file_path']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'project', 'name')
        }),
        ('File Information', {
            'fields': ('file_path', 'file_size', 'content_type')
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
