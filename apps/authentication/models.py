"""
API Client models for machine-to-machine authentication.
Secure storage of API keys for service accounts and client applications.
"""

import secrets
import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.tenants.models import Tenant


class APIClient(models.Model):
    """
    API Client model for machine-to-machine authentication.
    
    Stores client credentials (client_id + client_secret) for service accounts.
    Secrets are hashed and never stored in plaintext.
    
    Each API client belongs to a specific tenant and can have assigned roles/scopes.
    """
    
    # Primary identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique API client identifier")
    )
    
    # Client ID (public identifier, similar to username)
    client_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Public client identifier (like username)")
    )
    
    # Client secret (stored as hash, never plaintext)
    client_secret_hash = models.CharField(
        max_length=256,
        help_text=_("Hashed client secret (never stored in plaintext)")
    )
    
    # Display name for the client
    name = models.CharField(
        max_length=255,
        help_text=_("Human-readable name for this API client")
    )
    
    # Description/purpose of this client
    description = models.TextField(
        blank=True,
        help_text=_("Description of the client's purpose")
    )
    
    # Tenant association
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='api_clients',
        db_index=True,
        help_text=_("Tenant this API client belongs to")
    )
    
    # Status and enablement
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this API client is active and can authenticate")
    )
    
    # Token versioning for revocation
    token_version = models.IntegerField(
        default=1,
        help_text=_("Token version - increment to invalidate all existing tokens")
    )
    
    # Roles and scopes (stored as JSON for flexibility)
    roles = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of roles assigned to this client (e.g., ['read', 'write', 'admin'])")
    )
    
    scopes = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of scopes/permissions for this client")
    )
    
    # Rate limiting settings (optional, per-client overrides)
    rate_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Custom rate limit for this client (requests per hour)")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this API client was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this API client was last updated")
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this API client last authenticated")
    )
    
    # Security: IP whitelist (optional)
    allowed_ips = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of allowed IP addresses (empty = all IPs allowed)")
    )
    
    # Metadata for additional information
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata for this client")
    )
    
    class Meta:
        db_table = 'api_clients'
        verbose_name = _('API Client')
        verbose_name_plural = _('API Clients')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['is_active', 'last_used_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.client_id})"
    
    def __repr__(self):
        return f"<APIClient: {self.client_id} - tenant={self.tenant.slug}>"
    
    @staticmethod
    def generate_client_id(prefix='client'):
        """
        Generate a unique client ID.
        
        Format: prefix_<random_hex>
        Example: client_a1b2c3d4e5f6
        """
        random_part = secrets.token_hex(12)  # 24 characters
        return f"{prefix}_{random_part}"
    
    @staticmethod
    def generate_client_secret(length=32):
        """
        Generate a secure random client secret.
        
        Returns a URL-safe token that should be shown to the user once
        and then hashed before storage.
        """
        return secrets.token_urlsafe(length)
    
    def set_client_secret(self, raw_secret):
        """
        Hash and store the client secret.
        
        Args:
            raw_secret: The plaintext client secret
        """
        self.client_secret_hash = make_password(raw_secret)
    
    def verify_client_secret(self, raw_secret):
        """
        Verify a client secret against the stored hash.
        Uses constant-time comparison to prevent timing attacks.
        
        Args:
            raw_secret: The plaintext client secret to verify
            
        Returns:
            bool: True if the secret is valid, False otherwise
        """
        if not raw_secret or not self.client_secret_hash:
            return False
        
        return check_password(raw_secret, self.client_secret_hash)
    
    def revoke_tokens(self):
        """
        Revoke all existing tokens for this client by incrementing token_version.
        
        This invalidates all JWTs issued with the previous token_version.
        """
        self.token_version += 1
        self.save(update_fields=['token_version', 'updated_at'])
    
    def disable(self):
        """
        Disable this API client, preventing all authentication.
        """
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def enable(self):
        """
        Re-enable this API client.
        """
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
    
    def record_usage(self):
        """
        Record that this client was used (authenticated).
        """
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    def has_role(self, role):
        """
        Check if this client has a specific role.
        
        Args:
            role: Role name to check
            
        Returns:
            bool: True if the client has the role
        """
        return role in self.roles
    
    def has_scope(self, scope):
        """
        Check if this client has a specific scope.
        
        Args:
            scope: Scope name to check
            
        Returns:
            bool: True if the client has the scope
        """
        return scope in self.scopes
    
    def is_ip_allowed(self, ip_address):
        """
        Check if an IP address is allowed for this client.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            bool: True if IP is allowed (or no IP restrictions)
        """
        if not self.allowed_ips:
            return True  # No restrictions
        
        return ip_address in self.allowed_ips


class APIClientUsageLog(models.Model):
    """
    Audit log for API client authentication attempts.
    
    Records successful and failed authentication attempts for security monitoring.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    api_client = models.ForeignKey(
        APIClient,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        null=True,
        blank=True,
        help_text=_("The API client that attempted authentication")
    )
    
    client_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Client ID used in the attempt")
    )
    
    success = models.BooleanField(
        help_text=_("Whether the authentication attempt was successful")
    )
    
    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Reason for failure if authentication failed")
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address of the request")
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text=_("User agent string from the request")
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_("When the authentication attempt occurred")
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata about the attempt")
    )
    
    class Meta:
        db_table = 'api_client_usage_logs'
        verbose_name = _('API Client Usage Log')
        verbose_name_plural = _('API Client Usage Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['client_id', 'timestamp']),
            models.Index(fields=['api_client', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{status} - {self.client_id} at {self.timestamp}"
