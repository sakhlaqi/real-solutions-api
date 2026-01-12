"""
Tenant model and related models.
Central to the multi-tenant architecture.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Tenant(models.Model):
    """
    Tenant model - represents a single tenant in the multi-tenant system.
    
    All tenant-specific data must reference this model to ensure proper isolation.
    """
    
    # Unique identifier for the tenant (used in JWT token)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique tenant identifier")
    )
    
    # Human-readable tenant name
    name = models.CharField(
        max_length=255,
        help_text=_("Tenant organization name")
    )
    
    # Unique slug for tenant (can be used for display purposes)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("Unique tenant slug")
    )
    
    # Tenant status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether the tenant is active")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Tenant creation timestamp")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp")
    )
    
    # Optional: Tenant metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional tenant metadata")
    )
    
    class Meta:
        db_table = 'tenants'
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    def __repr__(self):
        return f"<Tenant: {self.slug} (id={self.id})>"
    
    def save(self, *args, **kwargs):
        """Override save to ensure slug is lowercase."""
        if self.slug:
            self.slug = self.slug.lower()
        super().save(*args, **kwargs)


class TenantAwareModel(models.Model):
    """
    Abstract base model for all tenant-scoped models.
    
    All models that need tenant isolation should inherit from this class.
    This ensures every record is tied to a specific tenant.
    """
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True,
        help_text=_("Tenant this record belongs to")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Record creation timestamp")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp")
    )
    
    class Meta:
        abstract = True
        # Enforce tenant-based ordering by default
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure tenant is always set.
        This provides an additional safeguard against cross-tenant data leaks.
        """
        if not self.tenant_id:
            raise ValueError(
                f"Tenant must be set for {self.__class__.__name__} instance"
            )
        super().save(*args, **kwargs)
