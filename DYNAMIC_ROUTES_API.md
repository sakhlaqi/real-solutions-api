# Dynamic Routes - API Implementation Guide

## Overview

The Django API now supports **dynamic routes configuration** for multi-tenant routing. Each tenant can define custom routes that are served to the presentation app via the tenant configuration endpoint.

## What Changed

### 1. Serializer Updates

**File:** `apps/tenants/serializers.py`

Added `routes` field to `TenantConfigSerializer`:
- Extracts routes from `tenant.metadata['routes']`
- Returns default routes if none configured
- Supports updating routes via API

### 2. Management Command

**File:** `apps/tenants/management/commands/configure_routes.py`

New command to easily configure tenant routes:

```bash
# Set default routes
python manage.py configure_routes <tenant-slug> --preset=default

# Set construction company routes
python manage.py configure_routes <tenant-slug> --preset=construction

# Set HR firm routes
python manage.py configure_routes <tenant-slug> --preset=hr

# List current routes
python manage.py configure_routes <tenant-slug> --list

# Clear all routes
python manage.py configure_routes <tenant-slug> --clear
```

## API Endpoints

### Get Tenant Configuration (with routes)

```http
GET /api/v1/tenants/{slug}/config/
```

**Response:**
```json
{
  "id": "uuid-here",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "is_active": true,
  "routes": [
    {
      "path": "/",
      "pagePath": "/",
      "title": "Home",
      "protected": false,
      "layout": "main",
      "order": 0
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
  "theme": { ... },
  "feature_flags": { ... },
  "created_at": "2026-01-25T00:00:00Z",
  "updated_at": "2026-01-25T00:00:00Z"
}
```

### Update Tenant Routes

```http
PATCH /api/v1/tenants/{slug}/config/
Content-Type: application/json
Authorization: Bearer <token>

{
  "routes": [
    {
      "path": "/admin/custom-page",
      "pagePath": "/custom-page",
      "title": "Custom Page",
      "protected": true,
      "layout": "admin"
    }
  ]
}
```

## Default Routes

If a tenant has no routes configured, these defaults are returned:

```python
[
    {
        'path': '/',
        'pagePath': '/',
        'title': 'Home',
        'protected': False,
        'layout': 'main',
        'order': 0
    },
    {
        'path': '/login',
        'pagePath': '/login',
        'title': 'Login',
        'protected': False,
        'layout': 'none',
        'order': 1
    },
    {
        'path': '/admin',
        'pagePath': '/dashboard',
        'title': 'Dashboard',
        'protected': True,
        'layout': 'admin',
        'order': 2
    }
]
```

## Route Configuration Schema

Each route object supports:

```python
{
    'path': str,              # React Router path (e.g., '/admin/projects/:id')
    'pagePath': str,          # Path to JSON page config
    'title': str,             # Page title
    'protected': bool,        # Requires authentication?
    'layout': str,            # Layout: 'main', 'admin', or 'none'
    'order': int,             # Optional: route priority
    'exact': bool,            # Optional: exact path matching
    'meta': dict,             # Optional: custom metadata
    'featureFlag': str        # Optional: feature flag name
}
```

## Usage Examples

### Example 1: Configure via Management Command

```bash
# Configure construction company routes
python manage.py configure_routes buildright --preset=construction

# Output:
# ✓ Successfully configured construction routes for BuildRight Construction
#   Total routes: 9
#   Routes configured:
#     🌐 / - Home
#     🌐 /login - Login
#     🔒 /admin - Dashboard
#     🔒 /admin/projects - Projects
#     🔒 /admin/equipment - Equipment
#     🔒 /admin/employees - Employees
```

### Example 2: Update via Django Admin

1. Go to Django Admin → Tenants → Select tenant
2. Edit `metadata` field (JSON)
3. Add routes array:

```json
{
  "branding": { ... },
  "theme": { ... },
  "routes": [
    {
      "path": "/admin/custom-report",
      "pagePath": "/custom-report",
      "title": "Custom Report",
      "protected": true,
      "layout": "admin"
    }
  ]
}
```

### Example 3: Update via API

```python
import requests

url = "http://localhost:8000/api/v1/tenants/acme-corp/config/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

data = {
    "routes": [
        {
            "path": "/admin/analytics",
            "pagePath": "/analytics",
            "title": "Analytics",
            "protected": True,
            "layout": "admin",
            "featureFlag": "analytics"
        }
    ]
}

response = requests.patch(url, json=data, headers=headers)
print(response.json())
```

### Example 4: Python Script

```python
from apps.tenants.models import Tenant

# Get tenant
tenant = Tenant.objects.get(slug='acme-corp')

# Add custom route
tenant.metadata['routes'] = [
    {
        'path': '/admin/inventory',
        'pagePath': '/inventory',
        'title': 'Inventory',
        'protected': True,
        'layout': 'admin'
    }
]

tenant.save()
```

## Setting Up Existing Tenants

### Option 1: Use Management Command (Recommended)

```bash
# List all tenants
python manage.py shell -c "from apps.tenants.models import Tenant; [print(f'{t.slug} - {t.name}') for t in Tenant.objects.all()]"

# Configure each tenant
python manage.py configure_routes tenant-1 --preset=default
python manage.py configure_routes tenant-2 --preset=construction
python manage.py configure_routes tenant-3 --preset=hr
```

### Option 2: Bulk Update Script

Create `scripts/setup_default_routes.py`:

```python
from apps.tenants.models import Tenant

DEFAULT_ROUTES = [
    {
        'path': '/',
        'pagePath': '/',
        'title': 'Home',
        'protected': False,
        'layout': 'main',
        'order': 0
    },
    {
        'path': '/login',
        'pagePath': '/login',
        'title': 'Login',
        'protected': False,
        'layout': 'none',
        'order': 1
    },
    {
        'path': '/admin',
        'pagePath': '/dashboard',
        'title': 'Dashboard',
        'protected': True,
        'layout': 'admin',
        'order': 2
    }
]

# Update all tenants without routes
for tenant in Tenant.objects.all():
    if 'routes' not in tenant.metadata or not tenant.metadata.get('routes'):
        tenant.metadata['routes'] = DEFAULT_ROUTES
        tenant.save()
        print(f'✓ Set default routes for {tenant.name}')
```

Run it:
```bash
python manage.py shell < scripts/setup_default_routes.py
```

## Testing

### Test API Endpoint

```bash
# Get tenant config (should include routes)
curl http://localhost:8000/api/v1/tenants/acme-corp/config/

# Expected response includes:
# {
#   ...
#   "routes": [
#     { "path": "/", "pagePath": "/", ... }
#   ]
# }
```

### Test Management Command

```bash
# List current routes
python manage.py configure_routes acme-corp --list

# Set construction routes
python manage.py configure_routes acme-corp --preset=construction

# Verify
curl http://localhost:8000/api/v1/tenants/acme-corp/config/ | grep -A 5 '"routes"'
```

### Test in Presentation App

1. Start Django API: `python manage.py runserver`
2. Start presentation app: `npm run dev`
3. Open browser console
4. Look for: `[useAppBootstrap] Loading dynamic routes from tenant config: X`

## Troubleshooting

### Routes Not Appearing

**Problem:** Frontend shows default routes only

**Solution:**
```bash
# Check if routes exist in tenant metadata
python manage.py configure_routes <tenant-slug> --list

# If empty, set routes
python manage.py configure_routes <tenant-slug> --preset=default
```

### API Returns Empty Routes Array

**Problem:** `"routes": []` in API response

**Cause:** Tenant metadata has empty routes array

**Solution:**
```python
# In Django shell
from apps.tenants.models import Tenant
tenant = Tenant.objects.get(slug='your-slug')

# Remove routes key to use defaults
if 'routes' in tenant.metadata:
    del tenant.metadata['routes']
    tenant.save()

# Or set explicitly
tenant.metadata['routes'] = [...]
tenant.save()
```

### CORS Issues

If frontend can't fetch tenant config:

```python
# config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True
```

## Database Schema

No migration needed! Routes are stored in the existing `metadata` JSONField:

```sql
SELECT 
    slug,
    name,
    metadata->'routes' as routes
FROM tenants
WHERE metadata ? 'routes';
```

## Performance Considerations

- Routes are cached in tenant metadata (no additional queries)
- JSON field indexed automatically
- Serializer method field has minimal overhead
- Frontend caches routes after initial load

## Security

✅ **Public endpoint:** `/tenants/{slug}/config/` is public (no auth required)
- Safe: Only returns configuration, not sensitive data
- Routes are just navigation structure

✅ **Update endpoint:** Requires authentication
- Only authenticated admins can update routes
- Tenant isolation enforced

## Next Steps

1. **Configure routes for all tenants**
   ```bash
   python manage.py configure_routes <slug> --preset=<type>
   ```

2. **Test API response**
   ```bash
   curl http://localhost:8000/api/v1/tenants/<slug>/config/
   ```

3. **Verify in frontend**
   - Check browser console for route loading logs
   - Navigate to admin pages
   - Verify custom routes work

4. **Create custom routes**
   - Use Django admin or API
   - Add feature flags as needed
   - Test protected vs public routes

## Summary

✅ Serializer updated to support routes  
✅ Management command for easy configuration  
✅ Default routes provided automatically  
✅ Multiple preset options available  
✅ API endpoints ready for frontend consumption  

Your Django API now fully supports dynamic, tenant-configurable routing!
