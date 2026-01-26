# CRUD API Endpoints Documentation

This document describes the new CRUD (Create, Read, Update, Delete) endpoints added for managing tenant configurations: Feature Flags, Routes, and Page Config.

## Overview

The API now provides full CRUD operations for three configuration resources:
1. **Feature Flags** - Boolean flags to enable/disable tenant features
2. **Routes** - Application routing configuration
3. **Page Config** - Page layout and component configuration

All endpoints are nested under `/api/v1/tenants/{tenant_id}/` and require authentication for mutations (POST, PATCH, PUT, DELETE).

## Backward Compatibility

The existing `/api/v1/tenants/{id}/config/` endpoint continues to work unchanged, returning a consolidated view of all configuration:

```http
GET /api/v1/tenants/{tenant_id}/config/
```

Response:
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "slug": "acme",
  "feature_flags": {
    "dark_mode": true,
    "analytics": true
  },
  "routes": [...],
  "page_config": {
    "version": "1.0.0",
    "pages": {...}
  }
}
```

## Feature Flags Endpoints

### List Feature Flags
```http
GET /api/v1/tenants/{tenant_id}/feature-flags/
```

**Authentication:** Not required for GET  
**Response:** Array of feature flag objects

```json
[
  {
    "id": "uuid",
    "tenant": "tenant-uuid",
    "key": "dark_mode",
    "enabled": true,
    "description": "Enable dark mode theme",
    "created_at": "2026-01-26T10:00:00Z",
    "updated_at": "2026-01-26T10:00:00Z"
  }
]
```

### Get Specific Feature Flag
```http
GET /api/v1/tenants/{tenant_id}/feature-flags/{flag_id}/
```

**Authentication:** Not required for GET  
**Response:** Single feature flag object

### Create Feature Flag
```http
POST /api/v1/tenants/{tenant_id}/feature-flags/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Permissions:** User must belong to the tenant

**Request Body:**
```json
{
  "key": "new_feature",
  "enabled": true,
  "description": "Description of the new feature"
}
```

**Response:** 201 Created
```json
{
  "id": "new-uuid",
  "tenant": "tenant-uuid",
  "key": "new_feature",
  "enabled": true,
  "description": "Description of the new feature",
  "created_at": "2026-01-26T10:00:00Z",
  "updated_at": "2026-01-26T10:00:00Z"
}
```

**Validation:**
- `key` must be unique per tenant
- `key` is required (max 100 characters)
- `enabled` defaults to `false` if not provided

### Update Feature Flag (Full)
```http
PUT /api/v1/tenants/{tenant_id}/feature-flags/{flag_id}/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Request Body:** All fields required
```json
{
  "key": "existing_feature",
  "enabled": false,
  "description": "Updated description"
}
```

### Update Feature Flag (Partial)
```http
PATCH /api/v1/tenants/{tenant_id}/feature-flags/{flag_id}/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Request Body:** Only fields to update
```json
{
  "enabled": false
}
```

### Delete Feature Flag
```http
DELETE /api/v1/tenants/{tenant_id}/feature-flags/{flag_id}/
```

**Authentication:** Required (JWT)  
**Response:** 204 No Content

---

## Routes Endpoints

### List Routes
```http
GET /api/v1/tenants/{tenant_id}/routes/
```

**Authentication:** Not required for GET  
**Response:** Array of route objects (ordered by `order` then `path`)

```json
[
  {
    "id": "uuid",
    "tenant": "tenant-uuid",
    "path": "/",
    "page_path": "/",
    "title": "Home",
    "exact": true,
    "protected": false,
    "layout": "DashboardLayout",
    "order": 0,
    "created_at": "2026-01-26T10:00:00Z",
    "updated_at": "2026-01-26T10:00:00Z"
  }
]
```

### Get Specific Route
```http
GET /api/v1/tenants/{tenant_id}/routes/{route_id}/
```

**Authentication:** Not required for GET  
**Response:** Single route object

### Create Route
```http
POST /api/v1/tenants/{tenant_id}/routes/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Permissions:** User must belong to the tenant

**Request Body:**
```json
{
  "path": "/dashboard",
  "page_path": "/dashboard",
  "title": "Dashboard",
  "exact": true,
  "protected": true,
  "layout": "DashboardLayout",
  "order": 10
}
```

**Response:** 201 Created

**Validation:**
- `path` must be unique per tenant
- `path` and `page_path` are required
- `order` defaults to `0`
- `exact` defaults to `true`
- `protected` defaults to `false`

### Update Route (Full)
```http
PUT /api/v1/tenants/{tenant_id}/routes/{route_id}/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Request Body:** All fields required

### Update Route (Partial)
```http
PATCH /api/v1/tenants/{tenant_id}/routes/{route_id}/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Request Body:** Only fields to update
```json
{
  "protected": true,
  "order": 5
}
```

### Delete Route
```http
DELETE /api/v1/tenants/{tenant_id}/routes/{route_id}/
```

**Authentication:** Required (JWT)  
**Response:** 204 No Content

---

## Page Config Endpoints

**Note:** Page Config is a singleton resource (OneToOne relationship with Tenant). There's only one page configuration per tenant.

### Get Page Config
```http
GET /api/v1/tenants/{tenant_id}/page-config/
```

**Authentication:** Not required for GET  
**Response:** Single page config object (not an array)

```json
{
  "id": "uuid",
  "tenant": "tenant-uuid",
  "version": "1.0.0",
  "pages": {
    "/": {
      "template": "DashboardLayout",
      "slots": {
        "main": [...]
      }
    },
    "/login": {...}
  },
  "created_at": "2026-01-26T10:00:00Z",
  "updated_at": "2026-01-26T10:00:00Z"
}
```

### Create Page Config
```http
POST /api/v1/tenants/{tenant_id}/page-config/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Permissions:** User must belong to the tenant

**Request Body:**
```json
{
  "version": "1.0.0",
  "pages": {
    "/": {
      "template": "DashboardLayout",
      "slots": {
        "main": [
          {
            "type": "Container",
            "children": []
          }
        ]
      }
    }
  }
}
```

**Response:** 201 Created

**Validation:**
- Each page must have `template` and `slots` fields
- Cannot create if page config already exists (use PATCH to update)
- `pages` must be a non-empty object

### Update Page Config (Full)
```http
PUT /api/v1/tenants/{tenant_id}/page-config/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Request Body:** All fields required

### Update Page Config (Partial)
```http
PATCH /api/v1/tenants/{tenant_id}/page-config/
Content-Type: application/json
```

**Authentication:** Required (JWT)  
**Request Body:** Only fields to update

**Example - Add a new page:**
```json
{
  "pages": {
    "/": {...existing pages...},
    "/new-page": {
      "template": "DashboardLayout",
      "slots": {
        "main": [...]
      }
    }
  }
}
```

### Delete Page Config
```http
DELETE /api/v1/tenants/{tenant_id}/page-config/
```

**Authentication:** Required (JWT)  
**Response:** 204 No Content

---

## Authentication

All mutation operations (POST, PATCH, PUT, DELETE) require:

1. **JWT Token** in Authorization header:
   ```
   Authorization: Bearer <token>
   ```

2. **Tenant Membership**: The authenticated user must belong to the tenant they're trying to modify.

### Getting a Token

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Error Responses

### 400 Bad Request
```json
{
  "key": ["Feature flag 'dark_mode' already exists for this tenant"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You can only create feature flags for your own tenant"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Examples

### Example: Toggle a Feature Flag

```bash
# 1. Get tenant ID
curl http://localhost:8000/api/v1/tenants/acme/

# 2. List feature flags
curl http://localhost:8000/api/v1/tenants/{tenant_id}/feature-flags/

# 3. Update specific flag (with auth)
curl -X PATCH \
  http://localhost:8000/api/v1/tenants/{tenant_id}/feature-flags/{flag_id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### Example: Add a New Route

```bash
curl -X POST \
  http://localhost:8000/api/v1/tenants/{tenant_id}/routes/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/settings",
    "page_path": "/settings",
    "title": "Settings",
    "exact": true,
    "protected": true,
    "layout": "DashboardLayout",
    "order": 20
  }'
```

### Example: Update Page Configuration

```bash
# Get current config
curl http://localhost:8000/api/v1/tenants/{tenant_id}/page-config/

# Update with new page (partial update)
curl -X PATCH \
  http://localhost:8000/api/v1/tenants/{tenant_id}/page-config/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pages": {
      "/": {...existing pages...},
      "/new-page": {
        "template": "DashboardLayout",
        "slots": {
          "main": [
            {
              "type": "Container",
              "children": [
                {
                  "type": "Card",
                  "props": {"title": "New Page"},
                  "children": []
                }
              ]
            }
          ]
        }
      }
    }
  }'
```

## Testing

Use the provided test scripts:

```bash
# Test serializers (no server needed)
python test_crud_endpoints.py

# Verify setup
python verify_crud_setup.py

# Test HTTP endpoints (server must be running)
python manage.py runserver
python test_api_endpoints.py
```

## Database Models

### TenantFeatureFlag
- `id`: UUID (Primary Key)
- `tenant`: ForeignKey to Tenant
- `key`: CharField(100) - unique per tenant
- `enabled`: Boolean
- `description`: TextField
- Indexes: (tenant, key), (tenant, enabled)

### TenantRoute  
- `id`: UUID (Primary Key)
- `tenant`: ForeignKey to Tenant
- `path`: CharField(255) - unique per tenant
- `page_path`: CharField(255)
- `title`, `exact`, `protected`, `layout`, `order`
- Indexes: (tenant, path), (tenant, order)

### TenantPageConfig
- `id`: UUID (Primary Key)
- `tenant`: OneToOne to Tenant
- `pages`: JSONField
- `version`: CharField(20)

## Migration History

1. **0005_add_config_tables.py** - Created initial table structures
2. **0006_migrate_metadata_to_tables.py** - Migrated data from metadata JSON
3. **0007_refactor_feature_flags_table.py** - Refactored flags to individual records
4. **0008_migrate_feature_flags_data.py** - Migrated flag data to new structure

## See Also

- [API_ENDPOINTS_IMPLEMENTATION.md](./API_ENDPOINTS_IMPLEMENTATION.md) - Implementation details
- [REFACTORING_CONFIG_TABLES.md](./REFACTORING_CONFIG_TABLES.md) - Refactoring documentation
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Migration guide
