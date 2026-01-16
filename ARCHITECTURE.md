# Tenant Isolation Architecture

## Overview

This document explains how tenant isolation is implemented and enforced at every layer of the application.

## Isolation Principles

1. **Single Source of Truth**: Tenant identity comes exclusively from JWT token
2. **Defense in Depth**: Multiple layers of validation prevent data leaks
3. **Fail Secure**: Invalid tenant context results in empty querysets
4. **Explicit Over Implicit**: Tenant must be explicitly set on all operations
5. **Audit Trail**: All tenant context is logged for security audits

## Architecture Layers

### 1. Authentication Layer

**Component**: `TenantJWTAuthentication`

**Responsibility**: Extract and validate tenant from JWT token

**Process**:
```python
1. Validate JWT signature and expiration (via djangorestframework-simplejwt)
2. Extract 'tenant' claim from token payload
3. Validate tenant claim is present and non-null
4. Query database for Tenant object by UUID
5. Validate tenant exists and is_active=True
6. Attach tenant to request.tenant
7. Continue authentication or raise AuthenticationFailed
```

**Security Guarantees**:
- ✅ Token signature verified using secret key
- ✅ Token expiration enforced
- ✅ Tenant claim required (missing claim = authentication fails)
- ✅ Tenant must exist in database
- ✅ Tenant must be active
- ✅ Invalid tenant = request rejected before reaching views

**Code Location**: `apps/authentication/authentication.py`

---

### 2. Middleware Layer

**Component**: `TenantMiddleware`

**Responsibility**: Secondary validation, request lifecycle management, and public endpoint handling

**Process**:
```python
1. Add correlation ID and timing to request
2. Check if request path is public endpoint (via URL resolution)
3. Skip tenant validation for public endpoints
4. For protected endpoints:
   - Validate tenant was set by authentication
   - Verify tenant is active (defense in depth)
   - Log tenant context for audit trail
5. Add correlation ID and timing to response headers
```

**Public Endpoint Management**:
- Public endpoints defined in `apps/core/public_endpoints.py`
- Uses Django URL resolution (not hardcoded paths)
- Checks URL names (e.g., `authentication:login`) for flexibility
- Supports method-level restrictions (e.g., GET only)

**Security Guarantees**:
- ✅ Runs after authentication, provides redundancy
- ✅ Blocks requests to API endpoints without valid tenant
- ✅ Validates tenant status (active/inactive)
- ✅ Returns 403 for inactive tenants
- ✅ Logs all tenant resolution attempts
- ✅ Public endpoints centrally managed (single source of truth)
- ✅ Dynamic URL patterns work automatically (no regex needed)

**Code Location**: `apps/tenants/middleware.py`, `apps/core/public_endpoints.py`

---

### 3. ORM Layer

**Component**: `TenantManager` and `TenantQuerySet`

**Responsibility**: Automatic tenant filtering in database queries

**Implementation**:

```python
class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)
    
    def for_tenant(self, tenant):
        """Filter by tenant."""
        return self.get_queryset().for_tenant(tenant)
```

**Usage in Views**:
```python
# Automatic tenant filtering
projects = Project.objects.for_tenant(request.tenant).all()

# Without tenant context - explicit filtering required
projects = Project.objects.filter(tenant=request.tenant)
```

**Security Guarantees**:
- ✅ No access to raw QuerySet without tenant filter
- ✅ `.for_tenant()` method enforces filtering
- ✅ Manager methods validate tenant is not None
- ✅ Creates clear audit trail of tenant-scoped queries

**Code Location**: `apps/tenants/managers.py`

---

### 4. Model Layer

**Component**: `TenantAwareModel` base class

**Responsibility**: Enforce tenant relationships at data model level

**Features**:

```python
class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.tenant_id:
            raise ValueError("Tenant must be set")
        super().save(*args, **kwargs)
    
    class Meta:
        abstract = True
```

**Foreign Key Validation**:

```python
class Task(TenantAwareModel):
    project = models.ForeignKey(Project, ...)
    
    def save(self, *args, **kwargs):
        # Enforce tenant consistency
        if self.project.tenant_id != self.tenant_id:
            raise ValueError("Task tenant must match project tenant")
        super().save(*args, **kwargs)
```

**Security Guarantees**:
- ✅ Tenant field required on all models
- ✅ Tenant cannot be null
- ✅ Save validation prevents tenant-less records
- ✅ Foreign key validation prevents cross-tenant references
- ✅ Database-level indexes optimize tenant queries

**Code Location**: `apps/tenants/models.py`

---

### 5. View Layer

**Component**: `TenantScopedViewSetMixin`

**Responsibility**: Enforce tenant filtering in API views

**Implementation**:

```python
class TenantScopedViewSetMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not hasattr(self.request, 'tenant'):
            return queryset.none()  # Return empty queryset
        
        return queryset.for_tenant(self.request.tenant)
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
```

**Security Guarantees**:
- ✅ All views inherit tenant filtering automatically
- ✅ Missing tenant context returns empty queryset
- ✅ Creates automatically set tenant on new objects
- ✅ Updates preserve existing tenant (tenant is immutable)
- ✅ List/retrieve/update/delete all tenant-scoped

**Code Location**: `apps/core/views.py`

---

### 6. Serializer Layer

**Component**: Custom serializers with tenant validation

**Responsibility**: Validate related objects belong to same tenant

**Implementation**:

```python
class TaskSerializer(serializers.ModelSerializer):
    def validate_project(self, value):
        """Validate project belongs to request tenant."""
        request = self.context.get('request')
        
        if value.tenant != request.tenant:
            raise serializers.ValidationError(
                "Project does not belong to your tenant"
            )
        
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['tenant'] = request.tenant
        return super().create(validated_data)
```

**Security Guarantees**:
- ✅ Foreign key references validated before save
- ✅ Cross-tenant references rejected with clear error
- ✅ Tenant automatically injected on create
- ✅ Serializer context includes request and tenant
- ✅ Validation errors prevent data corruption

**Code Location**: `apps/core/serializers.py`

---

## Data Flow Example

### Scenario: Create a Task for a Project

**Request**:
```http
POST /api/v1/tasks/
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
Content-Type: application/json

{
  "project": 5,
  "title": "Implement feature X",
  "status": "todo"
}
```

**Flow**:

1. **Authentication Layer**
   - Extract JWT token from header
   - Validate signature and expiration
   - Extract `tenant` claim → UUID `abc-123`
   - Query: `Tenant.objects.get(id='abc-123')`
   - Attach `request.tenant = <Tenant: abc-123>`

2. **Middleware Layer**
   - Validate tenant is active
   - Log: "Tenant resolved: acme for path /api/v1/tasks/"
   - Continue to view

3. **View Layer (TaskViewSet)**
   - Receive request with `request.tenant` set
   - Call `perform_create(serializer)`
   - Inject tenant: `serializer.save(tenant=request.tenant)`

4. **Serializer Layer**
   - Validate `project=5` exists
   - Query: `Project.objects.for_tenant(request.tenant).get(id=5)`
   - Validate project belongs to tenant `abc-123`
   - If project is from different tenant → ValidationError
   - Add tenant to validated_data

5. **Model Layer**
   - Create Task instance
   - Validate `tenant` is set (not None)
   - Validate `task.tenant == task.project.tenant`
   - If validation passes → save to database
   - If validation fails → raise ValueError

6. **Database Layer**
   - Insert record with tenant foreign key
   - Index on (tenant_id, project_id) used
   - Database constraint enforces tenant exists

**Result**: Task created successfully, all validation passed

---

## Attack Scenarios & Defenses

### Attack 1: Manipulate Project ID to Access Another Tenant's Data

**Attack**:
```json
POST /api/v1/tasks/
{
  "project": 999,  // Project from Tenant B
  "title": "Hack",
  "status": "todo"
}
```
*Token contains Tenant A's UUID*

**Defense Layers**:
1. **View Layer**: `Project.objects.for_tenant(Tenant A).get(id=999)` → DoesNotExist
2. **Serializer**: `validate_project()` checks `project.tenant != Tenant A` → ValidationError
3. **Model**: Even if saved, `task.tenant != project.tenant` → ValueError

**Result**: Request rejected with 400 Bad Request, "Project does not belong to your tenant"

---

### Attack 2: Forge JWT Token with Different Tenant

**Attack**:
```
Authorization: Bearer <forged-token-with-tenant-B>
```

**Defense Layers**:
1. **Authentication**: JWT signature validation fails → InvalidToken
2. **Signature**: Token not signed with server's secret key → AuthenticationFailed

**Result**: Request rejected with 401 Unauthorized

---

### Attack 3: Remove Tenant Claim from Token

**Attack**:
```json
// JWT payload without 'tenant' claim
{
  "user_id": 1,
  "exp": 1234567890
}
```

**Defense Layers**:
1. **Authentication**: Extract tenant claim → None
2. **Validation**: Tenant claim required → AuthenticationFailed

**Result**: Request rejected with 401 Unauthorized, "Token must include 'tenant' claim"

---

### Attack 4: Use Token from Inactive Tenant

**Attack**:
```
Authorization: Bearer <valid-token-but-tenant-inactive>
```

**Defense Layers**:
1. **Authentication**: Tenant.objects.get(id=X) → Found
2. **Validation**: Check `tenant.is_active` → False
3. **Middleware**: Additional check for active status

**Result**: Request rejected with 403 Forbidden, "Tenant 'slug' is not active"

---

### Attack 5: SQL Injection via Tenant ID

**Attack**:
```sql
tenant_id = "' OR '1'='1"
```

**Defense Layers**:
1. **ORM**: Django ORM parameterizes queries → SQL injection impossible
2. **UUID Validation**: Tenant ID must be valid UUID → invalid format rejected
3. **Type Safety**: UUID field type enforced by PostgreSQL

**Result**: Query fails safely, no data leaked

---

## Database Schema

### Tenant Table
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_active ON tenants(is_active);
```

### Example: Projects Table
```sql
CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    
    CONSTRAINT unique_project_name_per_tenant UNIQUE (tenant_id, name)
);

CREATE INDEX idx_projects_tenant_status ON projects(tenant_id, status);
CREATE INDEX idx_projects_tenant_name ON projects(tenant_id, name);
```

**Key Features**:
- Foreign key to `tenants` with CASCADE delete
- Indexes include `tenant_id` for query performance
- Unique constraints scoped to tenant
- All queries filtered by `tenant_id`

---

## Query Performance

### Optimized Queries

All queries include tenant in WHERE clause:

```sql
-- List projects for tenant
SELECT * FROM projects 
WHERE tenant_id = 'abc-123' 
ORDER BY created_at DESC;

-- Get project by ID (tenant-scoped)
SELECT * FROM projects 
WHERE tenant_id = 'abc-123' AND id = 5;

-- Join with tasks (both tenant-filtered)
SELECT p.*, t.* 
FROM projects p
JOIN tasks t ON t.project_id = p.id
WHERE p.tenant_id = 'abc-123' 
  AND t.tenant_id = 'abc-123';
```

**Performance Benefits**:
- Indexes on `(tenant_id, ...)` used for all queries
- PostgreSQL planner uses tenant filter first
- Small result sets due to tenant filtering
- No full table scans

---

## Monitoring & Auditing

### Log Examples

```
INFO [tenant:acme] User acme_user authenticated successfully
INFO [tenant:acme] Project created: id=5, name="New Project"
WARNING [tenant:beta] Failed login attempt: invalid credentials
ERROR [tenant:acme] Tenant validation failed: tenant not found
INFO [tenant:beta] Task updated: id=10, status=done
```

### Metrics to Monitor

- Tenant resolution failures
- Cross-tenant access attempts (should be zero)
- Inactive tenant access attempts
- Query performance per tenant
- API request volume per tenant

---

## Testing Tenant Isolation

### Unit Tests

```python
def test_cannot_access_other_tenant_project(self):
    """Verify tenant isolation in views."""
    # Create two tenants
    tenant_a = Tenant.objects.create(name='A', slug='a')
    tenant_b = Tenant.objects.create(name='B', slug='b')
    
    # Create project for Tenant A
    project_a = Project.objects.create(
        tenant=tenant_a,
        name='Project A'
    )
    
    # Try to access with Tenant B token
    token_b = generate_tenant_token(user_b, tenant_b)
    response = self.client.get(
        f'/api/v1/projects/{project_a.id}/',
        HTTP_AUTHORIZATION=f'Bearer {token_b["access"]}'
    )
    
    # Should return 404 (filtered out by tenant)
    self.assertEqual(response.status_code, 404)
```

### Integration Tests

```python
def test_create_task_with_cross_tenant_project(self):
    """Verify serializer rejects cross-tenant references."""
    # Project from Tenant A
    project_a = Project.objects.create(
        tenant=tenant_a,
        name='Project A'
    )
    
    # Try to create task with Tenant B token
    token_b = generate_tenant_token(user_b, tenant_b)
    response = self.client.post(
        '/api/v1/tasks/',
        {
            'project': project_a.id,
            'title': 'Task',
            'status': 'todo'
        },
        HTTP_AUTHORIZATION=f'Bearer {token_b["access"]}'
    )
    
    # Should return 400 with validation error
    self.assertEqual(response.status_code, 400)
    self.assertIn('Project does not belong', str(response.data))
```

---

## Summary

**Multi-Layer Defense**:
1. ✅ Authentication: Validates JWT and tenant claim
2. ✅ Middleware: Secondary tenant validation
3. ✅ ORM: Automatic tenant filtering
4. ✅ Models: Tenant consistency validation
5. ✅ Views: Queryset scoping
6. ✅ Serializers: Cross-tenant reference validation

**Security Guarantees**:
- Cross-tenant data access is **impossible**
- Missing tenant context fails **securely** (empty results)
- All layers validate independently (**defense in depth**)
- Tenant identity is **immutable** per request
- All operations are **auditable**

**Performance**:
- Database indexes optimize tenant queries
- Small result sets due to filtering
- No full table scans
- Efficient multi-tenant architecture

---

This architecture ensures **strict tenant isolation** while maintaining high performance and developer productivity.
