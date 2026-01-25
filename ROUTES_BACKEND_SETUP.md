# Backend Routes Configuration Example

## Django Model Update

Add routes field to your TenantConfiguration model:

```python
# api/apps/tenants/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField

class TenantConfiguration(models.Model):
    """Tenant-specific configuration"""
    
    tenant = models.OneToOneField(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # Existing fields
    branding = models.JSONField(default=dict)
    theme = models.JSONField(default=dict)
    feature_flags = models.JSONField(default=dict)
    layout_preferences = models.JSONField(default=dict)
    landing_page_sections = models.JSONField(default=list)
    
    # NEW: Dynamic routes configuration
    routes = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of route configurations for dynamic routing"
    )
    
    custom_settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'tenant_configurations'
        verbose_name = 'Tenant Configuration'
        verbose_name_plural = 'Tenant Configurations'
    
    def __str__(self):
        return f"Configuration for {self.tenant.name}"
```

## Example Routes Data

### Basic Setup (All Tenants)

```python
DEFAULT_ROUTES = [
    {
        "path": "/",
        "pagePath": "/",
        "title": "Home",
        "protected": False,
        "layout": "main",
        "order": 0
    },
    {
        "path": "/login",
        "pagePath": "/login",
        "title": "Login",
        "protected": False,
        "layout": "none",
        "order": 1
    },
    {
        "path": "/admin",
        "pagePath": "/dashboard",
        "title": "Dashboard",
        "protected": True,
        "layout": "admin",
        "order": 2
    }
]
```

### Construction Company Tenant

```python
CONSTRUCTION_ROUTES = [
    # Public routes
    {
        "path": "/",
        "pagePath": "/",
        "title": "Home",
        "protected": False,
        "layout": "main"
    },
    {
        "path": "/login",
        "pagePath": "/login",
        "title": "Login",
        "protected": False,
        "layout": "none"
    },
    
    # Admin routes
    {
        "path": "/admin",
        "pagePath": "/dashboard",
        "title": "Dashboard",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/projects",
        "pagePath": "/projects",
        "title": "Projects",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/projects/:id",
        "pagePath": "/projects/:id",
        "title": "Project Details",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/equipment",
        "pagePath": "/equipment",
        "title": "Equipment",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/employees",
        "pagePath": "/employees",
        "title": "Employees",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/timesheets",
        "pagePath": "/timesheets",
        "title": "Timesheets",
        "protected": True,
        "layout": "admin",
        "featureFlag": "timesheets"
    }
]
```

### HR Firm Tenant

```python
HR_FIRM_ROUTES = [
    # Public routes
    {
        "path": "/",
        "pagePath": "/",
        "title": "Home",
        "protected": False,
        "layout": "main"
    },
    {
        "path": "/login",
        "pagePath": "/login",
        "title": "Login",
        "protected": False,
        "layout": "none"
    },
    
    # Admin routes
    {
        "path": "/admin",
        "pagePath": "/dashboard",
        "title": "Dashboard",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/employees",
        "pagePath": "/employees",
        "title": "Employees",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/employees/:id",
        "pagePath": "/employees/:id",
        "title": "Employee Profile",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/payroll",
        "pagePath": "/payroll",
        "title": "Payroll",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/benefits",
        "pagePath": "/benefits",
        "title": "Benefits",
        "protected": True,
        "layout": "admin"
    },
    {
        "path": "/admin/recruiting",
        "pagePath": "/recruiting",
        "title": "Recruiting",
        "protected": True,
        "layout": "admin",
        "featureFlag": "recruiting"
    }
]
```

## Django Admin Setup

```python
# api/apps/tenants/admin.py
from django.contrib import admin
from .models import TenantConfiguration

@admin.register(TenantConfiguration)
class TenantConfigurationAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'route_count', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Routing', {
            'fields': ('routes',),
            'description': 'Configure dynamic routes for this tenant'
        }),
        ('Branding', {
            'fields': ('branding',),
            'classes': ('collapse',)
        }),
        ('Theme', {
            'fields': ('theme',),
            'classes': ('collapse',)
        }),
        ('Features', {
            'fields': ('feature_flags',),
            'classes': ('collapse',)
        }),
        ('Layout', {
            'fields': ('layout_preferences', 'landing_page_sections'),
            'classes': ('collapse',)
        }),
        ('Custom', {
            'fields': ('custom_settings',),
            'classes': ('collapse',)
        }),
    )
    
    def route_count(self, obj):
        return len(obj.routes) if obj.routes else 0
    route_count.short_description = 'Routes'
```

## Migration

```python
# api/apps/tenants/migrations/0XXX_add_routes.py
from django.db import migrations, models

def set_default_routes(apps, schema_editor):
    """Set default routes for existing tenants"""
    TenantConfiguration = apps.get_model('tenants', 'TenantConfiguration')
    
    default_routes = [
        {
            "path": "/",
            "pagePath": "/",
            "title": "Home",
            "protected": False,
            "layout": "main",
            "order": 0
        },
        {
            "path": "/login",
            "pagePath": "/login",
            "title": "Login",
            "protected": False,
            "layout": "none",
            "order": 1
        },
        {
            "path": "/admin",
            "pagePath": "/dashboard",
            "title": "Dashboard",
            "protected": True,
            "layout": "admin",
            "order": 2
        }
    ]
    
    for config in TenantConfiguration.objects.all():
        if not config.routes:
            config.routes = default_routes
            config.save()

class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0XXX_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantconfiguration',
            name='routes',
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.RunPython(set_default_routes),
    ]
```

## API Endpoint Test

```bash
# Get tenant config with routes
curl http://localhost:8000/api/v1/tenants/acme-corp/config/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "id": "tenant-123",
  "slug": "acme-corp",
  "name": "Acme Corporation",
  "routes": [
    {
      "path": "/",
      "pagePath": "/",
      "title": "Home",
      "protected": false,
      "layout": "main"
    },
    {
      "path": "/admin",
      "pagePath": "/dashboard",
      "title": "Dashboard",
      "protected": true,
      "layout": "admin"
    },
    {
      "path": "/admin/projects",
      "pagePath": "/projects",
      "title": "Projects",
      "protected": true,
      "layout": "admin"
    }
  ],
  "branding": { ... },
  "theme": { ... }
}
```

## Management Command

Create a management command to easily set up routes:

```python
# api/apps/tenants/management/commands/setup_routes.py
from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant, TenantConfiguration

class Command(BaseCommand):
    help = 'Set up default routes for a tenant'

    def add_arguments(self, parser):
        parser.add_argument('tenant_slug', type=str)
        parser.add_argument('--preset', type=str, default='default',
                          choices=['default', 'construction', 'hr'])

    def handle(self, *args, **options):
        tenant_slug = options['tenant_slug']
        preset = options['preset']
        
        try:
            tenant = Tenant.objects.get(slug=tenant_slug)
            config, _ = TenantConfiguration.objects.get_or_create(tenant=tenant)
            
            # Load preset routes
            if preset == 'construction':
                config.routes = CONSTRUCTION_ROUTES
            elif preset == 'hr':
                config.routes = HR_FIRM_ROUTES
            else:
                config.routes = DEFAULT_ROUTES
            
            config.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully set up {preset} routes for {tenant.name}'
                )
            )
            
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Tenant "{tenant_slug}" not found')
            )
```

Usage:
```bash
python manage.py setup_routes acme-corp --preset=construction
python manage.py setup_routes hr-solutions --preset=hr
```

## Testing

```python
# api/apps/tenants/tests/test_routes.py
from django.test import TestCase
from apps.tenants.models import Tenant, TenantConfiguration

class RoutesTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            slug='test-tenant',
            name='Test Tenant'
        )
        self.config = TenantConfiguration.objects.create(
            tenant=self.tenant
        )
    
    def test_default_routes(self):
        """Test that routes default to empty list"""
        self.assertEqual(self.config.routes, [])
    
    def test_set_routes(self):
        """Test setting routes"""
        routes = [
            {
                "path": "/",
                "pagePath": "/",
                "title": "Home",
                "protected": False,
                "layout": "main"
            }
        ]
        self.config.routes = routes
        self.config.save()
        
        self.config.refresh_from_db()
        self.assertEqual(len(self.config.routes), 1)
        self.assertEqual(self.config.routes[0]['path'], '/')
    
    def test_api_returns_routes(self):
        """Test that API endpoint returns routes"""
        self.config.routes = DEFAULT_ROUTES
        self.config.save()
        
        response = self.client.get(f'/api/v1/tenants/{self.tenant.slug}/config/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('routes', data)
        self.assertEqual(len(data['routes']), 3)
```

## Summary

To enable dynamic routing in your backend:

1. **Add `routes` field** to TenantConfiguration model
2. **Run migration** to add the field
3. **Set default routes** for existing tenants
4. **Configure routes** per tenant via Django admin or management command
5. **Test API** to ensure routes are returned in config

The frontend will automatically pick up these routes and generate the routing structure!
