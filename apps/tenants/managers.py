"""
Tenant-scoped managers and querysets.
Ensures all ORM queries are automatically filtered by tenant.

Security Model:
---------------
These managers provide the ORM-level defense for tenant isolation:
1. TenantQuerySet.for_tenant() - explicit tenant filtering
2. TenantManager.for_tenant() - manager-level filtering
3. TenantManager.create_for_tenant() - safe creation with tenant

Usage:
------
All tenant-scoped models should use TenantManager:

    class MyModel(TenantAwareModel):
        objects = TenantManager()
        
        class Meta:
            default_manager_name = 'objects'

Query patterns:
    # Always filter by tenant
    MyModel.objects.for_tenant(request.tenant).all()
    
    # Create with tenant
    MyModel.objects.create_for_tenant(request.tenant, name='example')
"""

from typing import Union, TYPE_CHECKING, Optional
from django.db import models
from django.core.exceptions import ValidationError
import uuid

if TYPE_CHECKING:
    from .models import Tenant


class TenantQuerySet(models.QuerySet):
    """
    Custom QuerySet that enforces tenant filtering.
    
    All queries should use for_tenant() to ensure proper isolation.
    """
    
    def for_tenant(self, tenant: Union['Tenant', uuid.UUID, str]) -> 'TenantQuerySet':
        """
        Filter queryset to a specific tenant.
        
        Args:
            tenant: Tenant instance, UUID, or UUID string
            
        Returns:
            QuerySet filtered by tenant
            
        Raises:
            ValidationError: If tenant is None
        """
        if tenant is None:
            raise ValidationError("Tenant cannot be None - this would leak data across tenants")
        
        # Handle Tenant objects, UUIDs, and UUID strings
        if hasattr(tenant, 'id'):
            tenant_id = tenant.id
        elif isinstance(tenant, str):
            tenant_id = uuid.UUID(tenant)
        else:
            tenant_id = tenant
            
        return self.filter(tenant_id=tenant_id)
    
    def active(self) -> 'TenantQuerySet':
        """Filter to active records only (if model has is_active field)."""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self
    
    def with_tenant(self) -> 'TenantQuerySet':
        """Prefetch tenant to avoid N+1 queries when accessing tenant."""
        return self.select_related('tenant')
    
    def only_essential(self) -> 'TenantQuerySet':
        """
        Select only essential fields for list views.
        Override in subclasses for model-specific field selection.
        """
        # Default: select id, tenant_id, and common fields
        essential_fields = ['id', 'tenant_id']
        
        # Add common fields if they exist
        for field in ['name', 'title', 'slug', 'status', 'is_active', 'created_at']:
            if hasattr(self.model, field):
                essential_fields.append(field)
        
        return self.only(*essential_fields)


class TenantManager(models.Manager):
    """
    Custom Manager that provides tenant-aware query methods.
    
    This manager should be used for all tenant-scoped models to ensure
    queries are automatically filtered by the current tenant context.
    """
    
    def get_queryset(self) -> TenantQuerySet:
        """Return the custom TenantQuerySet."""
        return TenantQuerySet(self.model, using=self._db)
    
    def for_tenant(self, tenant: Union['Tenant', uuid.UUID, str]) -> TenantQuerySet:
        """
        Get objects for a specific tenant.
        
        Usage:
            MyModel.objects.for_tenant(request.tenant).all()
        
        Args:
            tenant: Tenant instance, UUID, or UUID string
            
        Returns:
            QuerySet filtered by tenant
        """
        return self.get_queryset().for_tenant(tenant)
    
    def create_for_tenant(
        self, 
        tenant: Union['Tenant', uuid.UUID, str], 
        **kwargs
    ) -> models.Model:
        """
        Create an object for a specific tenant.
        
        This is a convenience method that automatically sets the tenant
        before creating the object.
        
        Args:
            tenant: Tenant instance, UUID, or UUID string
            **kwargs: Model field values
            
        Returns:
            Created model instance
            
        Raises:
            ValidationError: If tenant is None
        """
        if tenant is None:
            raise ValidationError("Tenant cannot be None - this would create orphaned data")
        
        kwargs['tenant'] = tenant
        return self.create(**kwargs)
    
    def get_or_create_for_tenant(
        self, 
        tenant: Union['Tenant', uuid.UUID, str], 
        defaults: Optional[dict] = None,
        **kwargs
    ) -> tuple[models.Model, bool]:
        """
        Get or create an object for a specific tenant.
        
        Args:
            tenant: Tenant instance, UUID, or UUID string
            defaults: Default values for creation
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (instance, created)
        """
        if tenant is None:
            raise ValidationError("Tenant cannot be None")
        
        defaults = defaults or {}
        defaults['tenant'] = tenant
        kwargs['tenant'] = tenant
        
        return self.get_or_create(defaults=defaults, **kwargs)
    
    def bulk_create_for_tenant(
        self,
        tenant: Union['Tenant', uuid.UUID, str],
        objs: list,
        **kwargs
    ) -> list:
        """
        Bulk create objects for a tenant.
        
        Ensures all objects have the tenant set before creation.
        
        Args:
            tenant: Tenant instance, UUID, or UUID string
            objs: List of model instances
            **kwargs: Additional arguments for bulk_create
            
        Returns:
            List of created instances
        """
        if tenant is None:
            raise ValidationError("Tenant cannot be None for bulk create")
        
        for obj in objs:
            obj.tenant = tenant
        
        return self.bulk_create(objs, **kwargs)
