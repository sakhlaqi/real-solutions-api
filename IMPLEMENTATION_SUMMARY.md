# API Client Authentication - Implementation Summary

## ✅ What Was Implemented

A comprehensive API key-based authentication system for Django REST Framework that supports machine-to-machine (M2M) communication and service accounts.

---

## 📦 New Files Created

### Models & Database
1. **`apps/authentication/models.py`**
   - `APIClient` model - Stores API clients with hashed secrets
   - `APIClientUsageLog` model - Audit log for authentication attempts
   - Methods for credential generation, verification, and token revocation

2. **`apps/authentication/migrations/0001_initial.py`**
   - Database migrations for APIClient and APIClientUsageLog tables

### Authentication & Security
3. **`apps/authentication/tokens.py`**
   - `APIClientAccessToken` - Custom access token with enhanced claims
   - `APIClientRefreshToken` - Custom refresh token
   - `create_token_pair_for_api_client()` - Token generation helper

4. **`apps/authentication/serializers.py`**
   - `APIClientTokenObtainSerializer` - Validates credentials, issues tokens
   - `APIClientRefreshSerializer` - Refresh token handling
   - `APIClientSerializer` - Read-only API client serialization
   - `APIClientCreateSerializer` - Create new API clients

5. **`apps/authentication/throttling.py`**
   - `APIClientTokenThrottle` - Rate limiting for token issuance (10/min)
   - `APIClientRefreshThrottle` - Rate limiting for refresh (30/min)
   - `PerClientRateThrottle` - Per-client custom rate limits

6. **`apps/authentication/authentication.py`** (updated)
   - `APIClientJWTAuthentication` - JWT authentication for API clients
   - Token version validation for revocation support

### Views & Endpoints
7. **`apps/authentication/views.py`** (updated)
   - `APIClientTokenObtainView` - POST /api/v1/auth/api-client/token/
   - `APIClientRefreshTokenView` - POST /api/v1/auth/api-client/token/refresh/

8. **`apps/authentication/urls.py`** (updated)
   - Added API client token endpoints

### Permissions
9. **`apps/authentication/permissions.py`** (updated)
   - `IsAPIClient` - Requires API client authentication
   - `HasAPIClientRole` - Check for specific roles
   - `HasAPIClientScope` - Check for specific scopes
   - `IsAPIClientOrUser` - Allow both API clients and users

### Admin Interface
10. **`apps/authentication/admin.py`**
    - Django admin interface for APIClient management
    - API client usage log viewer
    - Bulk actions: disable, enable, revoke tokens

### Management Commands
11. **`apps/authentication/management/commands/create_api_client.py`**
    - CLI command to create API clients
    - `python manage.py create_api_client --name "..." --tenant "..."`

### Documentation
12. **`API_CLIENT_AUTH.md`**
    - Complete authentication guide
    - Architecture overview
    - Setup instructions
    - API examples in multiple languages
    - Security best practices

13. **`API_CLIENT_QUICKSTART.md`**
    - Quick reference guide
    - Common commands and examples

14. **`test_api_client_auth.py`**
    - Test script demonstrating the complete flow
    - Creates test client, obtains tokens, makes requests

15. **`README.md`** (updated)
    - Added API client authentication section

---

## 🔧 Configuration Changes

### `config/settings.py`

**REST Framework:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.authentication.authentication.TenantJWTAuthentication',
        'apps.authentication.authentication.APIClientJWTAuthentication',  # NEW
    ],
    'DEFAULT_THROTTLE_RATES': {
        'api_client_token': '10/minute',      # NEW
        'api_client_refresh': '30/minute',    # NEW
        'per_client': '1000/hour',            # NEW
    },
}
```

**JWT Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Changed from 60
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    # Standard JWT claims
    'AUDIENCE': 'multitenant-api',
    'ISSUER': 'multitenant-api',
    'JTI_CLAIM': 'jti',
}
```

**API Client Settings:**
```python
API_CLIENT_TOKEN_RATE = '10/minute'
API_CLIENT_REFRESH_RATE = '30/minute'
PER_CLIENT_DEFAULT_RATE = '1000/hour'
```

---

## 🎯 Key Features Implemented

### ✅ Secure Credential Storage
- Client secrets hashed using Django's `make_password()` (PBKDF2)
- Constant-time comparison via `check_password()`
- Secrets never stored in plaintext

### ✅ JWT Best Practices
**Standard Claims:**
- `iss` (issuer) - API identifier
- `aud` (audience) - Target audience
- `sub` (subject) - API client UUID
- `exp` (expiration) - Token expiry
- `iat` (issued at) - Issuance timestamp
- `jti` (JWT ID) - Unique token identifier

**Custom Claims:**
- `client_id` - Public client identifier
- `client_type` - "service_account"
- `tenant_id` - Tenant UUID
- `tenant_slug` - Tenant slug
- `roles` - Array of roles
- `scopes` - Array of scopes/permissions
- `token_version` - For revocation

### ✅ Token Lifetimes
- **Access Token:** 15 minutes (short-lived)
- **Refresh Token:** 7 days (longer-lived)
- Configurable via environment variables

### ✅ Token Revocation
Two methods:
1. **Disable client** - `api_client.disable()` - Immediate revocation
2. **Increment version** - `api_client.revoke_tokens()` - Invalidate existing tokens

### ✅ Rate Limiting
- Token issuance: 10 requests/minute (prevents brute-force)
- Token refresh: 30 requests/minute
- Per-client: 1000 requests/hour (customizable per client)

### ✅ Audit Logging
- All authentication attempts logged
- Success/failure tracking
- IP address and user agent recorded
- Searchable in Django admin

### ✅ IP Whitelisting (Optional)
- Restrict API client access to specific IPs
- Empty whitelist = all IPs allowed

### ✅ Role-Based Access Control
- Assign roles (e.g., `['read', 'write', 'admin']`)
- Assign scopes (e.g., `['read:projects', 'write:projects']`)
- Permission classes for enforcement

### ✅ Tenant Isolation
- Each API client belongs to one tenant
- JWT tokens include tenant information
- Automatic tenant scoping in requests

### ✅ Production-Ready Security
- HTTPS-only in production
- Secure cookie settings
- HSTS enabled
- Constant-time secret comparison
- Rate limiting on authentication endpoints

---

## 🚀 Usage

### Create API Client
```bash
python manage.py create_api_client \
  --name "My Service Account" \
  --tenant "acme-corp" \
  --roles "read,write" \
  --scopes "read:projects,write:projects"
```

### Obtain Tokens
```bash
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_a1b2c3d4e5f6",
    "client_secret": "XyZ123AbC456..."
  }'
```

### Use Access Token
```bash
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

## 📊 Database Schema

### `api_clients` Table
```
- id (UUID, PK)
- client_id (VARCHAR(64), UNIQUE)
- client_secret_hash (VARCHAR(256))
- name (VARCHAR(255))
- description (TEXT)
- tenant_id (UUID, FK → tenants)
- is_active (BOOLEAN)
- token_version (INTEGER)
- roles (JSONB)
- scopes (JSONB)
- allowed_ips (JSONB)
- rate_limit (INTEGER, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- last_used_at (TIMESTAMP, nullable)
- metadata (JSONB)

Indexes:
- client_id
- tenant_id, is_active
- is_active, last_used_at
```

### `api_client_usage_logs` Table
```
- id (UUID, PK)
- api_client_id (UUID, FK → api_clients, nullable)
- client_id (VARCHAR(64))
- success (BOOLEAN)
- failure_reason (VARCHAR(255))
- ip_address (INET, nullable)
- user_agent (TEXT)
- timestamp (TIMESTAMP)
- metadata (JSONB)

Indexes:
- client_id, timestamp
- api_client_id, timestamp
- success, timestamp
```

---

## 🔐 Security Features

1. **Hashed Secrets** - PBKDF2 with Django's password hashers
2. **Constant-Time Comparison** - Prevents timing attacks
3. **Rate Limiting** - Aggressive limits on auth endpoints
4. **Audit Logging** - All attempts tracked
5. **IP Whitelisting** - Optional IP restrictions
6. **Token Versioning** - Revoke all tokens without disabling client
7. **Short-lived Tokens** - 15-minute access tokens
8. **HTTPS Only** - Enforced in production
9. **HSTS Headers** - HTTP Strict Transport Security
10. **Token Validation** - Comprehensive JWT claim validation

---

## 📝 Next Steps

### To Use:
1. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

2. **Create an API client:**
   ```bash
   python manage.py create_api_client --name "Test Client" --tenant "your-tenant"
   ```

3. **Test authentication:**
   ```bash
   python test_api_client_auth.py
   ```

### To Customize:
- Adjust token lifetimes in settings
- Configure rate limits per client
- Add custom roles and scopes
- Implement additional permission classes
- Add IP whitelisting for sensitive clients

---

## 📚 Documentation

- **Complete Guide:** [API_CLIENT_AUTH.md](./API_CLIENT_AUTH.md)
- **Quick Reference:** [API_CLIENT_QUICKSTART.md](./API_CLIENT_QUICKSTART.md)
- **Project README:** [README.md](./README.md)
- **API Examples:** [API_EXAMPLES.md](./API_EXAMPLES.md)

---

## ✅ All Requirements Met

✅ Django model for API clients / service accounts  
✅ Secure storage of secrets (hashed, never plaintext)  
✅ Token issuance endpoint that validates API keys and returns JWT  
✅ JWT best practices (iss, aud, sub, exp, iat, jti)  
✅ Embed tenant ID, roles/scopes in JWT claims  
✅ Short-lived access tokens, longer-lived refresh tokens  
✅ Token revocation via key disablement or token versioning  
✅ DRF authentication & permission enforcement  
✅ Rate limiting and constant-time secret comparison  
✅ HTTPS-only, production-ready defaults  
✅ Uses SimpleJWT, follows Django/DRF best practices  
✅ Clean and scalable solution  

---

**Implementation Complete! 🎉**
