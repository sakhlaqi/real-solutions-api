# UI Configuration API - Implementation Summary

## Overview

The UI Configuration is now **integrated into the main tenant config endpoint** for better performance. Instead of making two separate API calls, the presentation layer gets everything (routes, branding, theme, AND ui_config) in a single request.

## Endpoint

### GET /api/v1/tenants/{slug}/config/

**Public endpoint** - No authentication required

Returns the complete tenant configuration including UI pages.

**Response:**
```json
{
  "id": "...",
  "name": "Demo Company",
  "slug": "demo",
  "is_active": true,
  "branding": {...},
  "theme": {...},
  "feature_flags": {...},
  "layout_preferences": {...},
  "landing_page_sections": [...],
  "routes": [
    {
      "path": "/",
      "pagePath": "/home",
      "title": "Home",
      ...
    }
  ],
  "ui_config": {
    "pages": {
      "/home": {
        "template": "landing-page",
        "slots": {
          "header": {...},
          "hero": {...},
          "features": {...}
        }
      },
      "/login": {
        "template": "sign-in",
        "slots": {...}
      }
    },
    "version": "1.0.0"
  },
  "created_at": "...",
  "updated_at": "..."
}
```

### PATCH /api/v1/tenants/{slug}/config/

**Protected endpoint** - Requires JWT authentication and tenant ownership

Updates the tenant configuration including UI config.

**Request:**
```json
{
  "ui_config": {
    "pages": {
      "/custom": {
        "template": "landing-page",
        "slots": {...}
      }
    },
    "version": "1.1.0"
  }
}
```

## Why This Approach?

### ✅ **Benefits:**

1. **Single API Call** - Presentation app fetches everything on load
2. **Better Performance** - Fewer HTTP requests
3. **Consistency** - All tenant config in one place
4. **Simpler Frontend** - No need for separate hooks
5. **Atomic Updates** - Update routes and pages together

### ❌ **Old Approach (Removed):**

~~GET /api/v1/tenants/{slug}/ui-config/~~ ❌ Removed - ui_config is now part of /config/

## Implementation Details

### Storage

UI configurations are stored in the Tenant model's `metadata` JSONField alongside routes and other config:

```python
{
  "metadata": {
    "routes": [...],
    "ui_config": {
      "pages": {...},
      "version": "1.0.0"
    },
    "branding": {...},
    "theme": {...}
  }
}
```

### Serializer (apps/tenants/serializers.py)

The `TenantConfigSerializer` extracts `ui_config` from metadata:

```python
class TenantConfigSerializer(serializers.ModelSerializer):
    ui_config = serializers.SerializerMethodField()
    
    def get_ui_config(self, obj):
        """Extract UI configuration from metadata."""
        ui_config = obj.metadata.get('ui_config', {})
        
        # Default page if none configured
        default_pages = {
            '/': {
                'template': 'landing-page',
                'slots': {...}
            }
        }
        
        return {
            'pages': ui_config.get('pages', default_pages),
            'version': ui_config.get('version', '1.0.0'),
        }
```

### URL Configuration (apps/tenants/urls.py)

No changes needed - ui_config is now part of existing `/config/` endpoint:

```python
urlpatterns = [
    path('tenants/<slug:slug>/config/', TenantConfigBySlugView.as_view()),
]
```

## Management Command

### configure_ui

Configure UI pages for tenants with predefined templates.

**Usage:**

```bash
# Configure single tenant with specific template
python manage.py configure_ui --slug=demo --template=marketing

# Configure all tenants with default template
python manage.py configure_ui --all

# Available templates: default, marketing, saas, minimal
python manage.py configure_ui --slug=acme --template=saas
```

**Templates:**

1. **default** - Basic landing page with header, main content, footer
2. **marketing** - Full marketing site with hero, features, login/signup pages
3. **saas** - SaaS application pages with dashboard, settings
4. **minimal** - Minimal page with just main content

**Example:**

```bash
$ python manage.py configure_ui --slug=demo --template=marketing
✓ Configured demo with marketing template (3 pages)
```

This creates:
- `/` - Landing page with hero, features, footer
- `/login` - Sign-in page
- `/signup` - Sign-up page

## Integration with Presentation Layer

The presentation app's `useAppBootstrap` hook fetches the complete config on load:

```typescript
// presentation/src/hooks/useAppBootstrap.ts
export function useAppBootstrap() {
  const { tenant } = useAppStore();
  
  const { data, isLoading } = useQuery({
    queryKey: ['tenant-config', tenant.slug],
    queryFn: async () => {
      const response = await fetch(
        `/api/v1/tenants/${tenant.slug}/config/`
      );
      return await response.json();
    }
  });
  
  // data now includes:
  // - routes (for routing)
  // - ui_config.pages (for page rendering)
  // - branding, theme, etc.
  
  return { config: data, isLoading };
}
```

Then use `ui_config.pages` directly:

```typescript
// presentation/src/components/JsonPageRoute.tsx
function JsonPageRoute({ pagePath }: { pagePath: string }) {
  const { config } = useAppStore(); // Already loaded via useAppBootstrap
  
  const pageConfig = config.ui_config?.pages[pagePath];
  
  if (!pageConfig) {
    return <NotFound />;
  }
  
  return <PageRenderer {...pageConfig} />;
}
```

**Flow:**

1. User visits `/login`
2. DynamicRoutes matches route to pagePath `/login`
3. JsonPageRoute looks up `config.ui_config.pages['/login']`
4. PageRenderer renders template with slots

**No additional API calls needed!** ✨

## Testing

### Test GET endpoint:

```bash
# Get complete config including ui_config
curl http://localhost:8000/api/v1/tenants/demo/config/ | python -m json.tool

# Extract just ui_config
curl -s http://localhost:8000/api/v1/tenants/demo/config/ | python -m json.tool | grep -A 50 '"ui_config"'

# Get Acme config
curl http://localhost:8000/api/v1/tenants/acme/config/ | python -m json.tool
```

### Test with different tenants:

```bash
# Configure acme tenant with SaaS template
python manage.py configure_ui --slug=acme --template=saas

# Fetch acme configuration (includes ui_config)
curl http://localhost:8000/api/v1/tenants/acme/config/ | jq '.ui_config'
```

### Test PATCH endpoint:

```bash
# Get auth token first
TOKEN="your-jwt-token"

# Update tenant config including ui_config
curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ui_config": {
      "pages": {
        "/custom": {
          "template": "landing-page",
          "slots": {...}
        }
      },
      "version": "1.1.0"
    }
  }' \
  http://localhost:8000/api/v1/tenants/demo/config/
```

## Default Behavior

If a tenant doesn't have ui_config set, the serializer returns a default landing page:

```json
{
  "ui_config": {
    "pages": {
      "/": {
        "template": "landing-page",
        "slots": {
          "header": {
            "component": "Navbar",
            "props": {"logo": "/logo.png", "links": []}
          },
          "main": {
            "component": "Container",
            "props": {
              "children": [
                {
                  "component": "Heading",
                  "props": {"level": 1, "text": "Welcome to {tenant.name}"}
                }
              ]
            }
          },
          "footer": {
            "component": "Footer",
            "props": {"copyright": "© 2026 {tenant.name}"}
          }
        }
      }
    },
    "version": "1.0.0"
  }
}
```

## Related Files

- **Serializer**: `api/apps/tenants/serializers.py` (TenantConfigSerializer.get_ui_config)
- **View**: `api/apps/tenants/views.py` (TenantConfigBySlugView)
- **URLs**: `api/apps/tenants/urls.py`
- **Management Command**: `api/apps/tenants/management/commands/configure_ui.py`
- **Model**: `api/apps/tenants/models.py` (Tenant.metadata)
- **Frontend Hook**: `presentation/src/hooks/useAppBootstrap.ts`
- **Documentation**: `presentation/TEMPLATE_ROUTING_GUIDE.md`

## Next Steps

1. ✅ ui_config integrated into /config/ endpoint
2. ✅ Management command created
3. ✅ Demo and Acme tenants configured
4. ⏳ Update presentation app to use config.ui_config instead of separate call
5. ⏳ Add caching for performance
6. ⏳ Add versioning support for A/B testing
7. ⏳ Create UI admin panel for editing pages

## Changelog

### 2026-01-25 (v2 - Consolidated)
- ✅ Integrated ui_config into main /config/ endpoint
- ✅ Removed separate /ui-config/ endpoint for better performance
- ✅ Added get_ui_config() to TenantConfigSerializer
- ✅ Single API call now returns everything (routes + pages + branding + theme)
- ✅ Simplified frontend integration

### 2026-01-25 (v1 - Initial)
- ✅ Created TenantUiConfigView with GET and PATCH methods (deprecated)
- ✅ Added URL route for /tenants/{slug}/ui-config/ (removed)
- ✅ Created configure_ui management command
- ✅ Added 4 template types (default, marketing, saas, minimal)
- ✅ Tested with demo tenant
- ✅ Integrated with presentation layer documentation
