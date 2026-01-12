# System Architecture Diagrams

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Web App     │  │  Mobile App  │  │  Service     │     │
│  │  (React)     │  │  (iOS/Android)│  │  (Internal)  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                     JWT Token with                           │
│                     'tenant' claim                           │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY / LOAD BALANCER              │
│                    (Nginx / AWS ALB)                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│               DJANGO API SERVICE (Multi-Tenant)             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Authentication Layer                          │  │
│  │  • Validate JWT signature                            │  │
│  │  • Extract 'tenant' claim                            │  │
│  │  • Resolve Tenant object                             │  │
│  │  • Attach to request.tenant                          │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Middleware Layer                              │  │
│  │  • Validate tenant is active                         │  │
│  │  • Log tenant context                                │  │
│  │  • Block invalid tenants                             │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         View Layer (DRF)                              │  │
│  │  • ProjectViewSet                                    │  │
│  │  • TaskViewSet                                       │  │
│  │  • DocumentViewSet                                   │  │
│  │  • Auto-filter by request.tenant                     │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         ORM Layer (Django)                            │  │
│  │  • TenantManager                                     │  │
│  │  • Tenant-scoped queries                             │  │
│  │  • Automatic filtering                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ▼                                        │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  POSTGRESQL DATABASE                         │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ tenants  │  │ projects │  │  tasks   │  │documents │  │
│  │          │  │          │  │          │  │          │  │
│  │ • id (PK)│◄─┤tenant_id │◄─┤tenant_id │◄─┤tenant_id │  │
│  │ • name   │  │  (FK)    │  │  (FK)    │  │  (FK)    │  │
│  │ • slug   │  │ • name   │  │ • title  │  │ • name   │  │
│  │ • active │  │ • status │  │ • status │  │ • path   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  • All tenant queries use indexes: (tenant_id, ...)         │
│  • Foreign key constraints enforce referential integrity    │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Lifecycle

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. HTTP Request
       │    Authorization: Bearer <jwt-token>
       ▼
┌─────────────────────────────────────┐
│   TenantJWTAuthentication           │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 1. Validate JWT signature   │  │
│   │ 2. Check expiration         │  │
│   │ 3. Extract 'tenant' claim   │  │
│   │    → tenant_id = "abc-123"  │  │
│   └─────────────────────────────┘  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 4. Query database:          │  │
│   │    Tenant.objects.get(      │  │
│   │      id='abc-123'           │  │
│   │    )                        │  │
│   └─────────────────────────────┘  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 5. Validate tenant.is_active│  │
│   │    ✓ Active                 │  │
│   └─────────────────────────────┘  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 6. Attach to request:       │  │
│   │    request.tenant = tenant  │  │
│   └─────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   TenantMiddleware                  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 1. Verify request.tenant    │  │
│   │    exists                   │  │
│   │ 2. Check tenant.is_active   │  │
│   │ 3. Log tenant context       │  │
│   └─────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   ProjectViewSet                    │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ get_queryset():             │  │
│   │   return Project.objects    │  │
│   │     .for_tenant(            │  │
│   │       request.tenant        │  │
│   │     )                       │  │
│   └─────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   TenantManager                     │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ for_tenant(tenant):         │  │
│   │   return self.filter(       │  │
│   │     tenant_id=tenant.id     │  │
│   │   )                         │  │
│   └─────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PostgreSQL Query                  │
│                                     │
│   SELECT * FROM projects            │
│   WHERE tenant_id = 'abc-123'       │
│   ORDER BY created_at DESC          │
│                                     │
│   [Uses Index: idx_projects_tenant] │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Serializer                        │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ ProjectSerializer           │  │
│   │   • Serialize data          │  │
│   │   • Add computed fields     │  │
│   │   • Return JSON             │  │
│   └─────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────┐
│   JSON Response      │
│                      │
│   {                  │
│     "count": 2,      │
│     "results": [     │
│       {              │
│         "id": 1,     │
│         "name": "...",│
│         ...          │
│       }              │
│     ]                │
│   }                  │
└──────────────────────┘
```

---

## Data Model Relationships

```
┌──────────────────────┐
│      Tenant          │
│                      │
│ • id (UUID) PK       │
│ • name               │
│ • slug (unique)      │
│ • is_active          │
│ • created_at         │
│ • metadata (JSON)    │
└──────────┬───────────┘
           │
           │ One-to-Many
           │
     ┌─────┴─────┬─────────────┬──────────────┐
     │           │             │              │
     ▼           ▼             ▼              ▼
┌────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐
│Project │  │  Task  │  │ Document │  │  (Other) │
│        │  │        │  │          │  │          │
│• tenant│  │• tenant│  │• tenant  │  │• tenant  │
│  (FK)  │  │  (FK)  │  │  (FK)    │  │  (FK)    │
│• name  │  │• title │  │• name    │  │• ...     │
│• status│  │• status│  │• path    │  │          │
└────┬───┘  └───┬────┘  └──────────┘  └──────────┘
     │          │
     │          │ Many-to-One
     │          │
     └──────────┼────────►
                │
         Task.project (FK)
```

**Key Constraints:**
- Every model has `tenant` foreign key
- Foreign keys must reference objects from same tenant
- Unique constraints scoped to tenant
- Indexes include tenant_id for performance

---

## Tenant Isolation Layers

```
                    ┌─────────────────┐
                    │   JWT Token     │
                    │ (tenant claim)  │
                    └────────┬────────┘
                             │
    ┌────────────────────────┴────────────────────────┐
    │                                                  │
    ▼                                                  ▼
┌───────────────────────┐                  ┌─────────────────────┐
│ Layer 1: Auth         │                  │ Layer 2: Middleware │
│ • JWT validation      │ ────────────────►│ • Active check      │
│ • Tenant extraction   │                  │ • Context logging   │
│ • request.tenant      │                  │ • Block invalid     │
└───────┬───────────────┘                  └──────────┬──────────┘
        │                                             │
        │            ┌────────────────────────────────┘
        │            │
        ▼            ▼
    ┌─────────────────────────────────────────────┐
    │       Layer 3: View (DRF)                   │
    │ • TenantScopedViewSetMixin                  │
    │ • get_queryset() filters by tenant          │
    │ • perform_create() sets tenant              │
    └──────────────────┬──────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────┐
    │       Layer 4: ORM (Django)                 │
    │ • TenantManager.for_tenant()                │
    │ • Automatic WHERE tenant_id = ?             │
    │ • Returns tenant-scoped QuerySet            │
    └──────────────────┬──────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────┐
    │       Layer 5: Model                        │
    │ • TenantAwareModel base class               │
    │ • save() validates tenant not null          │
    │ • FK validation checks same tenant          │
    └──────────────────┬──────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────┐
    │       Layer 6: Database                     │
    │ • Foreign key constraints                   │
    │ • Indexes on (tenant_id, ...)               │
    │ • Physical data isolation                   │
    └─────────────────────────────────────────────┘

          All layers enforce tenant isolation!
```

---

## Authentication Flow

```
┌────────────────────────────────────────────────────────────┐
│  1. User Login                                              │
└─────────────────────────┬──────────────────────────────────┘
                          │
    POST /api/v1/auth/token/
    {
      "username": "user@acme.com",
      "password": "password123"
    }
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  2. Backend Validation                                      │
│     • Verify username/password                             │
│     • Determine user's tenant                              │
└─────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  3. Generate JWT Token with Tenant Claim                   │
│                                                             │
│    JWT Payload:                                            │
│    {                                                        │
│      "user_id": 123,                                       │
│      "tenant": "abc-123-uuid",  ← CRITICAL                 │
│      "exp": 1640000000,                                    │
│      "iat": 1639990000,                                    │
│      "iss": "multitenant-api",                             │
│      "aud": "multitenant-api"                              │
│    }                                                        │
│                                                             │
│    Signed with SECRET_KEY                                  │
└─────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  4. Return Tokens                                           │
│     {                                                       │
│       "access": "eyJ0eXAi...",                             │
│       "refresh": "eyJ0eXAi..."                             │
│     }                                                       │
└─────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  5. Client Stores Token                                     │
│     • localStorage / secure storage                         │
│     • Include in Authorization header                       │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  6. Subsequent Requests                                     │
│                                                             │
│     GET /api/v1/projects/                                  │
│     Authorization: Bearer eyJ0eXAi...                      │
└─────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  7. TenantJWTAuthentication                                 │
│     • Decode JWT                                            │
│     • Extract tenant claim                                  │
│     • Resolve Tenant("abc-123-uuid")                       │
│     • Attach to request.tenant                             │
└─────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  8. Return Tenant-Scoped Data                               │
│     Only projects for Tenant "abc-123-uuid"                │
└────────────────────────────────────────────────────────────┘
```

---

## Security Attack Prevention

```
┌──────────────────────────────────────────────────────────┐
│  Attack 1: Manipulate Project ID                         │
│                                                           │
│  Attacker (Tenant A) tries to access Tenant B project:  │
│                                                           │
│  GET /api/v1/projects/999/                               │
│  Authorization: Bearer <tenant-a-token>                  │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  Defense:                                                   │
│  1. Auth extracts tenant_id = "tenant-a"                   │
│  2. View filters: Project.objects.for_tenant(tenant_a)     │
│  3. Query: WHERE id=999 AND tenant_id='tenant-a'           │
│  4. Result: DoesNotExist → 404 Not Found                   │
│                                                             │
│  ✓ Tenant B project is invisible to Tenant A               │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Attack 2: Forge JWT Token                               │
│                                                           │
│  Attacker creates fake token with tenant_id="tenant-b"  │
│  Authorization: Bearer <forged-token>                    │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  Defense:                                                   │
│  1. JWT signature validation fails                         │
│  2. Token not signed with server's SECRET_KEY              │
│  3. Result: 401 Unauthorized                               │
│                                                             │
│  ✓ Cannot forge valid tokens without secret key            │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Attack 3: Remove Tenant Claim                           │
│                                                           │
│  Attacker creates token without 'tenant' claim           │
│  Authorization: Bearer <token-without-tenant>            │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  Defense:                                                   │
│  1. TenantJWTAuthentication checks for tenant claim        │
│  2. No tenant claim found                                  │
│  3. Result: 401 Unauthorized                               │
│  4. Error: "Token must include 'tenant' claim"             │
│                                                             │
│  ✓ Tenant claim is mandatory                               │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Attack 4: Cross-Tenant Foreign Key                      │
│                                                           │
│  Attacker (Tenant A) tries to create task with          │
│  project from Tenant B                                   │
│                                                           │
│  POST /api/v1/tasks/                                     │
│  { "project": <tenant-b-project-id>, ... }               │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  Defense:                                                   │
│  1. Serializer validate_project() runs                     │
│  2. Check: project.tenant == request.tenant                │
│  3. Result: ValidationError                                │
│  4. Error: "Project does not belong to your tenant"        │
│                                                             │
│  ✓ Cross-tenant references blocked by serializer           │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Load Balancer  │
                  │   (AWS ALB /    │
                  │    Nginx)       │
                  └────────┬────────┘
                           │
        ┏━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┓
        ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐
│  Django Server 1 │                  │  Django Server 2 │
│                  │                  │                  │
│  • Gunicorn      │                  │  • Gunicorn      │
│  • 4 workers     │                  │  • 4 workers     │
│  • Auto-scaling  │                  │  • Auto-scaling  │
└────────┬─────────┘                  └────────┬─────────┘
         │                                     │
         └──────────────┬──────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   PostgreSQL     │
              │   (RDS / Managed)│
              │                  │
              │  • Primary       │
              │  • Read Replicas │
              │  • Backups       │
              └──────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SUPPORTING SERVICES                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Redis   │  │  Sentry  │  │CloudWatch│  │   S3      │  │
│  │ (Cache)  │  │ (Errors) │  │  (Logs)  │  │(Static)   │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

These diagrams illustrate the multi-layered architecture that ensures **strict tenant isolation** while maintaining high performance and scalability.
