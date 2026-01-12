"""
Tenant-scoped managers and querysets.
Ensures all ORM queries are automatically filtered by tenant.
"""

from django.db import models
from django.core.exceptions import ValidationError


class TenantQuerySet(models.QuerySet):
    """
    Custom QuerySet that enforces tenant filtering.
    """
    
    def for_tenant(self, tenant):
        """
        Filter queryset to a specific tenant.
        
        Args:
            tenant: Tenant instance or tenant ID
            
        Returns:
            QuerySet filtered by tenant
        """
        if tenant is None:
            raise ValidationError("Tenant cannot be None")
        
        # Handle both Tenant objects and UUIDs
        tenant_id = getattr(tenant, 'id', tenant)
        return self.filter(tenant_id=tenant_id)


class TenantManager(models.Manager):
    """
    Custom Manager that provides tenant-aware query methods.
    
    This manager should be used for all tenant-scoped models to ensure
    queries are automatically filtered by the current tenant context.
    """
    
    def get_queryset(self):
        """Return the custom TenantQuerySet."""
        return TenantQuerySet(self.model, using=self._db)
    
    def for_tenant(self, tenant):
        """
        Get objects for a specific tenant.
        
        Usage:
            MyModel.objects.for_tenant(request.tenant).all()
        
        Args:
            tenant: Tenant instance or tenant ID
            
        Returns:
            QuerySet filtered by tenant
        """
        return self.get_queryset().for_tenant(tenant)
    
    def create_for_tenant(self, tenant, **kwargs):
        """
        Create an object for a specific tenant.
        
        This is a convenience method that automatically sets the tenant
        before creating the object.
        
        Args:
            tenant: Tenant instance or tenant ID
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        if tenant is None:
            raise ValidationError("Tenant cannot be None")
        
        kwargs['tenant'] = tenant
        return self.create(**kwargs)
