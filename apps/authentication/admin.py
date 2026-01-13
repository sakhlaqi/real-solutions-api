"""
Django admin configuration for authentication models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import APIClient, APIClientUsageLog


@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    """
    Admin interface for API clients.
    """
    
    list_display = [
        'name',
        'client_id',
        'tenant',
        'is_active_badge',
        'roles_display',
        'scopes_display',
        'last_used_at',
        'created_at',
    ]
    
    list_filter = [
        'is_active',
        'tenant',
        'created_at',
        'last_used_at',
    ]
    
    search_fields = [
        'name',
        'client_id',
        'description',
        'tenant__name',
        'tenant__slug',
    ]
    
    readonly_fields = [
        'id',
        'client_id',
        'client_secret_hash',
        'created_at',
        'updated_at',
        'last_used_at',
    ]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'client_id', 'name', 'description', 'tenant')
        }),
        (_('Status'), {
            'fields': ('is_active', 'token_version', 'last_used_at')
        }),
        (_('Permissions'), {
            'fields': ('roles', 'scopes')
        }),
        (_('Security'), {
            'fields': ('client_secret_hash', 'allowed_ips', 'rate_limit')
        }),
        (_('Metadata'), {
            'fields': ('metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['disable_clients', 'enable_clients', 'revoke_tokens']
    
    def is_active_badge(self, obj):
        """Display active status as colored badge."""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 10px; border-radius: 3px;">Disabled</span>'
        )
    is_active_badge.short_description = _('Status')
    
    def roles_display(self, obj):
        """Display roles as badges."""
        if not obj.roles:
            return '-'
        badges = [
            f'<span style="background-color: #007bff; color: white; '
            f'padding: 2px 8px; border-radius: 3px; margin-right: 3px;">{role}</span>'
            for role in obj.roles
        ]
        return format_html(''.join(badges))
    roles_display.short_description = _('Roles')
    
    def scopes_display(self, obj):
        """Display scopes count."""
        count = len(obj.scopes) if obj.scopes else 0
        return f"{count} scope(s)"
    scopes_display.short_description = _('Scopes')
    
    @admin.action(description=_('Disable selected API clients'))
    def disable_clients(self, request, queryset):
        """Disable selected API clients."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            _(f'{count} API client(s) disabled successfully.')
        )
    
    @admin.action(description=_('Enable selected API clients'))
    def enable_clients(self, request, queryset):
        """Enable selected API clients."""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            _(f'{count} API client(s) enabled successfully.')
        )
    
    @admin.action(description=_('Revoke all tokens for selected clients'))
    def revoke_tokens(self, request, queryset):
        """Revoke all tokens for selected API clients."""
        count = 0
        for client in queryset:
            client.revoke_tokens()
            count += 1
        self.message_user(
            request,
            _(f'Tokens revoked for {count} API client(s).')
        )


@admin.register(APIClientUsageLog)
class APIClientUsageLogAdmin(admin.ModelAdmin):
    """
    Admin interface for API client usage logs.
    """
    
    list_display = [
        'timestamp',
        'client_id',
        'success_badge',
        'failure_reason',
        'ip_address',
    ]
    
    list_filter = [
        'success',
        'timestamp',
        'api_client',
    ]
    
    search_fields = [
        'client_id',
        'ip_address',
        'failure_reason',
        'user_agent',
    ]
    
    readonly_fields = [
        'id',
        'api_client',
        'client_id',
        'success',
        'failure_reason',
        'ip_address',
        'user_agent',
        'timestamp',
        'metadata',
    ]
    
    fieldsets = (
        (_('Authentication Attempt'), {
            'fields': ('timestamp', 'api_client', 'client_id', 'success', 'failure_reason')
        }),
        (_('Request Details'), {
            'fields': ('ip_address', 'user_agent')
        }),
        (_('Metadata'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def success_badge(self, obj):
        """Display success status as colored badge."""
        if obj.success:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">SUCCESS</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 10px; border-radius: 3px;">FAILED</span>'
        )
    success_badge.short_description = _('Result')
    
    def has_add_permission(self, request):
        """Disable manual creation of usage logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Usage logs are read-only."""
        return False
