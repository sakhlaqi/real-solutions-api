"""
Tenant model and related models.
Central to the multi-tenant architecture.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid
import json

from .validators import validate_theme_json

User = get_user_model()


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
    
    # Theme selection
    theme = models.ForeignKey(
        'Theme',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants_using',
        help_text=_("Selected theme for this tenant")
    )
    
    theme_modes = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Enabled theme modes (e.g., ['dark', 'compact'])")
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
            models.Index(fields=['theme']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    def __repr__(self):
        return f"<Tenant: {self.slug} (id={self.id})>"
    
    def clean(self):
        """Validate tenant data before saving."""
        super().clean()
        
        # Validate theme selection
        if self.theme:
            # Can only select presets or custom themes owned by this tenant
            if not self.theme.is_preset and self.theme.tenant != self:
                raise ValidationError(
                    "Can only select preset themes or custom themes owned by this tenant"
                )
        
        # Validate theme_modes
        if self.theme and self.theme_modes:
            available_modes = list(self.theme.theme_json.get('modes', {}).keys())
            for mode in self.theme_modes:
                if mode not in available_modes:
                    raise ValidationError(
                        f"Theme mode '{mode}' is not available in selected theme. "
                        f"Available modes: {', '.join(available_modes)}"
                    )
    
    def save(self, *args, **kwargs):
        """Override save to ensure slug is lowercase and run validation."""
        if self.slug:
            self.slug = self.slug.lower()
        
        # Run validation
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def get_theme_metadata(self):
        """
        Get theme metadata without full theme JSON.
        Returns lightweight theme info for API responses.
        """
        if not self.theme:
            return None
        
        resolved = self.theme.get_resolved_theme_json()
        meta = resolved.get('meta', {})
        modes = list(resolved.get('modes', {}).keys())
        
        metadata = {
            'id': str(self.theme.id),
            'name': self.theme.name,
            'version': self.theme.version,
            'is_preset': self.theme.is_preset,
            'category': meta.get('category'),
            'available_modes': modes,
            'selected_modes': self.theme_modes,
        }
        
        # Add inheritance info if theme extends a preset
        inheritance = self.theme.get_inheritance_info()
        if inheritance:
            metadata['based_on'] = inheritance['base_preset']
            metadata['has_overrides'] = inheritance['has_overrides']
        
        return metadata
    
    def get_resolved_theme(self):
        """
        Get the full resolved theme JSON for this tenant.
        If theme uses inheritance, returns merged tokens.
        """
        if not self.theme:
            return None
        
        return self.theme.get_resolved_theme_json()


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


class Theme(models.Model):
    """
    Theme model - stores theme presets and custom themes.
    
    Themes can be:
    1. Global presets (isPreset=True, tenant=None) - read-only, official themes
    2. Tenant-specific custom themes (isPreset=False, tenant=Tenant)
    
    Theme data is stored as JSON conforming to the UI library schema.
    """
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique theme identifier")
    )
    
    # Theme name (must match themeJson.meta.name for consistency)
    name = models.CharField(
        max_length=255,
        help_text=_("Theme name")
    )
    
    # Theme version (semver format)
    version = models.CharField(
        max_length=20,
        default='1.0.0',
        help_text=_("Theme version (semantic versioning)")
    )
    
    # Preset flag - true for official themes from UI library
    is_preset = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether this is an official preset theme")
    )
    
    # Theme JSON data - conforms to UI library Theme schema
    theme_json = models.JSONField(
        help_text=_("Complete theme definition in JSON format")
    )
    
    # Optional: Tenant owner (null for global presets)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='themes',
        help_text=_("Tenant that owns this theme (null for presets)")
    )
    
    # Creator (null for system-seeded presets)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_themes',
        help_text=_("User who created this theme")
    )
    
    # Theme inheritance - for custom themes based on presets
    base_preset = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_themes',
        help_text=_("Base preset this theme extends (null for standalone themes)")
    )
    
    # Token overrides - only changed tokens (merged with base at runtime)
    token_overrides = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Token overrides to apply over base preset (empty for standalone themes)")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Theme creation timestamp")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp")
    )
    
    class Meta:
        db_table = 'themes'
        verbose_name = _('Theme')
        verbose_name_plural = _('Themes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_preset']),
            models.Index(fields=['tenant']),
            models.Index(fields=['name']),
        ]
        constraints = [
            # Presets must not have a tenant
            models.CheckConstraint(
                check=(
                    models.Q(is_preset=True, tenant__isnull=True) |
                    models.Q(is_preset=False)
                ),
                name='preset_themes_no_tenant'
            ),
            # Unique name per tenant (presets share global namespace)
            models.UniqueConstraint(
                fields=['name', 'tenant'],
                name='unique_theme_name_per_tenant'
            ),
        ]
    
    def __str__(self):
        preset_label = " [PRESET]" if self.is_preset else ""
        tenant_label = f" ({self.tenant.slug})" if self.tenant else ""
        return f"{self.name} v{self.version}{preset_label}{tenant_label}"
    
    def __repr__(self):
        return f"<Theme: {self.name} v{self.version} (preset={self.is_preset})>"
    
    def clean(self):
        """Validate theme data before saving."""
        super().clean()
        
        # Validate theme_json structure (only for standalone themes)
        if not self.base_preset:
            # Standalone theme - must have complete theme_json
            if not self.theme_json:
                raise ValidationError("theme_json cannot be empty for standalone themes")
            
            # Use comprehensive validator
            try:
                validate_theme_json(self.theme_json)
            except ValidationError as e:
                # Re-raise with more context
                raise ValidationError(f"Invalid theme_json: {e}")
            
            # Ensure required fields exist in theme_json
            meta = self.theme_json.get('meta', {})
            
            # Sync name and version with meta
            theme_name = meta.get('name')
            theme_version = meta.get('version')
            
            if self.name != theme_name:
                raise ValidationError(
                    f"Theme name '{self.name}' must match theme_json.meta.name '{theme_name}'"
                )
            
            if self.version != theme_version:
                raise ValidationError(
                    f"Theme version '{self.version}' must match theme_json.meta.version '{theme_version}'"
                )
        else:
            # Inherited theme - validate base_preset and overrides
            if self.base_preset.tenant is not None:
                raise ValidationError("base_preset must be a preset theme (tenant must be None)")
            
            if not self.base_preset.is_preset:
                raise ValidationError("base_preset must be a preset theme (is_preset must be True)")
            
            # Inherited themes can have minimal theme_json (just meta) or use base_preset's
            # token_overrides contains the customizations
        
        # Presets cannot have a tenant
        if self.is_preset and self.tenant:
            raise ValidationError("Preset themes cannot be associated with a tenant")
        
        # Custom themes must have a tenant
        if not self.is_preset and not self.tenant:
            raise ValidationError("Non-preset themes must be associated with a tenant")
        
        # Presets cannot extend other themes
        if self.is_preset and self.base_preset:
            raise ValidationError("Preset themes cannot extend other themes")
        
        # Circular inheritance check
        if self.base_preset and self.base_preset.base_preset:
            raise ValidationError("Only one level of inheritance is supported")
    
    def save(self, *args, **kwargs):
        """Override save to enforce validation."""
        # Run full_clean to trigger clean() method
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_read_only(self):
        """Check if theme is read-only (presets are read-only)."""
        return self.is_preset
    
    def get_resolved_theme_json(self):
        """
        Get the complete resolved theme JSON.
        For inherited themes, merges base_preset.theme_json with token_overrides.
        For standalone themes, returns theme_json as-is.
        """
        if not self.base_preset:
            # Standalone theme - return as-is
            return self.theme_json
        
        # Inherited theme - merge base + overrides
        from .utils import deep_merge_tokens
        
        base_theme = self.base_preset.theme_json
        
        # Get meta from theme_json if exists, otherwise create default
        if self.theme_json and 'meta' in self.theme_json:
            meta = self.theme_json['meta']
        else:
            # Create default meta based on base preset
            base_meta = base_theme.get('meta', {})
            meta = {
                'id': base_meta.get('id', str(self.id)),
                'name': self.name,
                'version': self.version,
                'category': 'custom',
                'description': f"Based on {self.base_preset.name}",
                'based_on': {
                    'id': str(self.base_preset.id),
                    'name': self.base_preset.name,
                    'version': self.base_preset.version
                }
            }
        
        # Build complete theme JSON
        resolved = {
            'meta': meta,
            'tokens': deep_merge_tokens(
                base_theme.get('tokens', {}),
                self.token_overrides
            ),
            'modes': base_theme.get('modes', {})  # Inherit modes from base
        }
        
        return resolved
    
    def get_inheritance_info(self):
        """Get information about theme inheritance."""
        if not self.base_preset:
            return None
        
        return {
            'base_preset': {
                'id': str(self.base_preset.id),
                'name': self.base_preset.name,
                'version': self.base_preset.version
            },
            'has_overrides': bool(self.token_overrides),
            'override_count': self._count_overrides(self.token_overrides)
        }
    
    def _count_overrides(self, obj):
        """Recursively count number of overridden tokens."""
        count = 0
        if isinstance(obj, dict):
            for value in obj.values():
                count += self._count_overrides(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_overrides(item)
        else:
            # Leaf value - count it
            count = 1
        return count
    
    @classmethod
    def get_presets(cls):
        """Get all preset themes."""
        return cls.objects.filter(is_preset=True).order_by('name')
    
    @classmethod
    def get_tenant_themes(cls, tenant):
        """Get all themes for a specific tenant (custom + presets)."""
        return cls.objects.filter(
            models.Q(tenant=tenant) | models.Q(is_preset=True)
        ).order_by('-is_preset', 'name')
