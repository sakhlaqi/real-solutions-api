# Changelog

All notable changes to the Real Solutions API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-15

### Added

#### New Files
- **`apps/core/constants.py`** - Centralized application constants
  - `JWTClaims` - Standardized JWT claim names
  - `ClientType`, `AuthType` - Authentication type identifiers
  - `ProjectStatus`, `TaskStatus`, `TaskPriority` - Business domain enums
  - `APIScopes`, `APIRoles` - Permission constants
  - `ErrorMessages` - Standardized error messages
  - `PaginationDefaults` - Default pagination settings

#### New Exception Classes
- `TenantInactiveError` - For inactive tenant access attempts
- `ResourceNotFoundError` - For missing resources with custom messages
- `TokenRevokedError` - For revoked token authentication attempts

#### New Manager Methods
- `TenantManager.get_or_create_for_tenant()` - Safe get-or-create with tenant
- `TenantManager.bulk_create_for_tenant()` - Bulk create with tenant validation
- `TenantQuerySet.with_tenant()` - Prefetch tenant for N+1 prevention
- `TenantQuerySet.only_essential()` - Select minimal fields for list views
- `TenantQuerySet.active()` - Filter to active records

#### New Serializer
- `ProjectListSerializer` - Optimized serializer for list views using annotated counts

### Changed

#### Security Enhancements
- **`config/settings.py`**
  - Added production validation that **requires** `SECRET_KEY` via environment variable
  - Prevents deployment with insecure default key
  - Provides clear error message with key generation instructions

#### Authentication Improvements
- **`apps/authentication/authentication.py`**
  - Fixed inconsistent tenant claim extraction (`tenant` vs `tenant_id`)
  - All authentication classes now use `JWTClaims.TENANT` constant
  - Added type hints for better code clarity (`Token`, `Tuple`, `Any`)
  - Optimized database queries with `.only()` for tenant lookups
  - Consistent error messages using `ErrorMessages` constants

- **`apps/authentication/permissions.py`**
  - Enhanced `IsTenantUser` with comprehensive documentation
  - Added `_validate_tenant_access()` method for custom implementations
  - Added logging for missing tenant context
  - Improved type hints (`Request`, `APIView`)

#### Middleware Refactoring
- **`apps/tenants/middleware.py`**
  - **Removed:** Duplicate token validation (now handled by authentication class)
  - **Added:** Request correlation ID (`X-Correlation-ID`) for distributed tracing
  - **Added:** Response timing header (`X-Response-Time`)
  - **Added:** Cached public paths for O(1) lookup
  - **Added:** Compiled regex patterns for dynamic routes
  - Clean separation of concerns between middleware and authentication

#### Performance Optimizations
- **`apps/core/views.py`**
  - Fixed N+1 queries with `annotate(tasks_count=Count('tasks'))`
  - Added `select_related('tenant')` for related lookups
  - Optimized statistics endpoint with single aggregation query
  - Added `get_serializer_class()` to use list serializer for list actions
  - Added fail-safe empty queryset when no tenant context

- **`apps/core/serializers.py`**
  - `ProjectListSerializer` uses annotated counts (no N+1)
  - Improved cross-tenant validation using `tenant_id` comparison
  - Better error messages for security violations
  - Defensive checks for missing tenant context in `create()`

#### Manager Improvements
- **`apps/tenants/managers.py`**
  - Added comprehensive security documentation
  - Improved type hints using `TYPE_CHECKING`
  - Better error messages for None tenant scenarios
  - Support for UUID strings in tenant filtering

#### Exception Handling
- **`apps/core/exceptions.py`**
  - Standardized error response format
  - Correlation ID inclusion in error responses
  - Appropriate logging levels (error for 5xx, warning for 4xx)
  - Returns generic message for unhandled exceptions

### API Response Format

All error responses now follow this standardized format:

```json
{
    "error": {
        "code": "error_code",
        "message": "Human-readable message",
        "details": { "field": "error details" }
    },
    "status_code": 400,
    "tenant": "tenant-slug",
    "correlation_id": "uuid"
}
```

### Response Headers

New response headers added:
- `X-Correlation-ID` - Request tracking for distributed systems
- `X-Response-Time` - Request processing duration in milliseconds

### Security Architecture

Defense-in-depth tenant isolation is enforced at 6 layers:
1. **Authentication** - JWT tenant claim extraction
2. **Middleware** - Tenant validation and logging
3. **Permission** - `IsTenantUser` validates tenant context
4. **View** - `TenantScopedViewSetMixin` filters querysets
5. **Serializer** - Validates cross-tenant references
6. **Model** - `TenantAwareModel.save()` enforces tenant

### Migration Notes

No database migrations required for this release.

#### Breaking Changes
None. All changes are backward compatible.

#### Deprecations
- `tenant_id` JWT claim is deprecated in favor of `tenant`
- Both are supported for backward compatibility

---

## [1.0.0] - Initial Release

- Multi-tenant Django API with JWT authentication
- API client authentication support
- Tenant-scoped models and managers
- Core models: Project, Task, Document
