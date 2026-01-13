# API Client Authentication Guide

## Overview

This Django REST Framework application supports **API key-based authentication** for machine-to-machine (M2M) communication and service accounts. API clients can authenticate using `client_id` + `client_secret` credentials to obtain JWT access and refresh tokens.

## Features

✅ **Secure Credential Storage** - Client secrets are hashed using Django's password hashers (never stored in plaintext)  
✅ **JWT Best Practices** - Tokens include standard claims: `iss`, `aud`, `sub`, `exp`, `iat`, `jti`  
✅ **Tenant Isolation** - Each API client belongs to a specific tenant  
✅ **Role-Based Access Control** - Assign roles and scopes to API clients  
✅ **Token Revocation** - Disable clients or increment token version to invalidate tokens  
✅ **Rate Limiting** - Configurable rate limits per client and per endpoint  
✅ **IP Whitelisting** - Optional IP address restrictions  
✅ **Audit Logging** - All authentication attempts are logged  
✅ **Constant-Time Comparison** - Prevents timing attacks on secrets  
✅ **Production-Ready** - HTTPS-only, secure defaults

---

## Architecture

### Models

#### `APIClient`
Represents a service account or machine client with:
- `client_id` - Public identifier (like a username)
- `client_secret_hash` - Hashed secret (never plaintext)
- `tenant` - Associated tenant
- `roles` - List of assigned roles (e.g., `['read', 'write', 'admin']`)
- `scopes` - List of permissions (e.g., `['read:projects', 'write:projects']`)
- `token_version` - For token revocation
- `is_active` - Enable/disable the client
- `allowed_ips` - IP whitelist (optional)
- `rate_limit` - Custom rate limit (optional)

#### `APIClientUsageLog`
Audit log for authentication attempts:
- Success/failure status
- Timestamp
- IP address
- User agent
- Failure reason

### Token Structure

JWT tokens issued to API clients include:

**Standard Claims:**
- `iss` (issuer) - API issuer identifier
- `aud` (audience) - API audience identifier
- `sub` (subject) - API client UUID
- `exp` (expiration) - Token expiration time
- `iat` (issued at) - Token issuance time
- `jti` (JWT ID) - Unique token identifier

**Custom Claims:**
- `client_id` - API client identifier
- `client_type` - Always `"service_account"`
- `tenant_id` - Tenant UUID
- `tenant_slug` - Tenant slug
- `roles` - Array of roles
- `scopes` - Array of scopes
- `token_version` - For revocation support
- `token_type` - `"access"` or `"refresh"`

---

## Setup

### 1. Run Migrations

```bash
python manage.py migrate authentication
```

### 2. Create an API Client

Using the management command:

```bash
python manage.py create_api_client \
  --name "My Service Account" \
  --tenant "acme-corp" \
  --description "Service account for automated tasks" \
  --roles "read,write" \
  --scopes "read:projects,write:projects" \
  --rate-limit 5000
```

**Output:**
```
======================================================================
API Client Created Successfully
======================================================================

Name:        My Service Account
Tenant:      ACME Corp (acme-corp)
ID:          a1b2c3d4-e5f6-7890-abcd-ef1234567890

CLIENT CREDENTIALS (save these securely):
----------------------------------------------------------------------
Client ID:     client_a1b2c3d4e5f6
Client Secret: XyZ123AbC456DeF789...
----------------------------------------------------------------------

⚠️  IMPORTANT: Save these credentials now!
The client secret cannot be retrieved later.

Roles:       read, write
Scopes:      read:projects, write:projects
Rate Limit:  5000 requests/hour
```

**⚠️ Security Note:** The client secret is shown only once. Store it securely!

---

## Authentication Flow

### 1. Obtain JWT Tokens

Exchange client credentials for JWT tokens:

**Endpoint:** `POST /api/v1/auth/api-client/token/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_a1b2c3d4e5f6",
    "client_secret": "XyZ123AbC456DeF789..."
  }'
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_token_expires_at": 1704067200,
  "refresh_token_expires_at": 1704672000,
  "token_type": "Bearer"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication failed"
}
```

### 2. Use Access Token

Include the access token in the `Authorization` header:

```bash
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Refresh Access Token

When the access token expires, use the refresh token to get a new one:

**Endpoint:** `POST /api/v1/auth/api-client/token/refresh/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_token_expires_at": 1704067200,
  "token_type": "Bearer"
}
```

---

## Token Lifetimes

Default configuration:

- **Access Token:** 15 minutes (short-lived for security)
- **Refresh Token:** 7 days (longer-lived for convenience)

Configure via environment variables:
```bash
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

---

## Rate Limiting

### Default Rates

- **Token Issuance:** 10 requests/minute (prevents brute-force attacks)
- **Token Refresh:** 30 requests/minute
- **Per-Client Default:** 1000 requests/hour

### Custom Rate Limits

Set custom rate limits per client:

```bash
python manage.py create_api_client \
  --name "High-Volume Service" \
  --tenant "acme-corp" \
  --rate-limit 10000
```

### Rate Limit Headers

Rate limit information is included in response headers:
- `X-RateLimit-Limit` - Total allowed requests
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Time when limit resets

---

## IP Whitelisting

Restrict API client access to specific IP addresses:

```bash
python manage.py create_api_client \
  --name "Internal Service" \
  --tenant "acme-corp" \
  --allowed-ips "10.0.1.5,10.0.1.6,192.168.1.100"
```

If no IPs are specified, all IPs are allowed.

---

## Roles & Scopes

### Roles

Coarse-grained permissions assigned to API clients:

```python
roles = ['read', 'write', 'admin']
```

### Scopes

Fine-grained permissions for specific operations:

```python
scopes = ['read:projects', 'write:projects', 'delete:projects']
```

### Permission Enforcement

Use permission classes in your views:

```python
from rest_framework.views import APIView
from apps.authentication.permissions import (
    IsAPIClient,
    HasAPIClientRole,
    HasAPIClientScope
)

class ProjectListView(APIView):
    permission_classes = [IsAPIClient, HasAPIClientScope]
    required_scopes = ['read:projects']
    
    def get(self, request):
        # Only API clients with 'read:projects' scope can access
        projects = Project.objects.filter(tenant=request.tenant)
        return Response(...)
```

---

## Token Revocation

### Method 1: Disable Client

Immediately revoke all tokens by disabling the client:

```python
from apps.authentication.models import APIClient

api_client = APIClient.objects.get(client_id='client_a1b2c3d4e5f6')
api_client.disable()
```

### Method 2: Increment Token Version

Invalidate all existing tokens while keeping the client active:

```python
api_client.revoke_tokens()
```

This increments `token_version`, causing token validation to fail for old tokens.

---

## Security Features

### 1. Hashed Secrets

Client secrets are hashed using Django's `make_password()` (PBKDF2 by default):

```python
api_client.set_client_secret(raw_secret)  # Hashes before storing
api_client.verify_client_secret(raw_secret)  # Constant-time comparison
```

### 2. Constant-Time Comparison

Secret verification uses `check_password()` which performs constant-time comparison to prevent timing attacks.

### 3. HTTPS Only (Production)

In production (`DEBUG=False`), the following security settings are enabled:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### 4. Audit Logging

All authentication attempts are logged:

```python
from apps.authentication.models import APIClientUsageLog

# Query failed attempts
failed_attempts = APIClientUsageLog.objects.filter(
    client_id='client_a1b2c3d4e5f6',
    success=False
)
```

### 5. Rate Limiting

Aggressive rate limiting on authentication endpoints prevents brute-force attacks.

---

## Permission Classes

### `IsAPIClient`
Requires API client authentication:

```python
permission_classes = [IsAPIClient]
```

### `HasAPIClientRole`
Requires specific role(s):

```python
permission_classes = [IsAPIClient, HasAPIClientRole]
required_roles = ['admin', 'write']  # Client needs ANY of these
```

### `HasAPIClientScope`
Requires specific scope(s):

```python
permission_classes = [IsAPIClient, HasAPIClientScope]
required_scopes = ['read:projects', 'write:projects']
```

### `IsAPIClientOrUser`
Allows both API clients and regular users:

```python
permission_classes = [IsAPIClientOrUser]
```

---

## Integration Examples

### Python Requests

```python
import requests

# Get tokens
response = requests.post(
    'http://localhost:8000/api/v1/auth/api-client/token/',
    json={
        'client_id': 'client_a1b2c3d4e5f6',
        'client_secret': 'XyZ123AbC456DeF789...'
    }
)

tokens = response.json()
access_token = tokens['access']

# Use access token
headers = {'Authorization': f'Bearer {access_token}'}
projects = requests.get(
    'http://localhost:8000/api/v1/projects/',
    headers=headers
).json()
```

### JavaScript/Node.js

```javascript
// Get tokens
const response = await fetch('http://localhost:8000/api/v1/auth/api-client/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_id: 'client_a1b2c3d4e5f6',
    client_secret: 'XyZ123AbC456DeF789...'
  })
});

const tokens = await response.json();

// Use access token
const projects = await fetch('http://localhost:8000/api/v1/projects/', {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
}).then(res => res.json());
```

### cURL

```bash
# Get tokens
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{"client_id":"client_a1b2c3d4e5f6","client_secret":"XyZ123AbC456DeF789..."}')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access')

# Use access token
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Environment Variables

Configure JWT settings via environment variables:

```bash
# JWT Token Lifetimes
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# JWT Issuer/Audience
JWT_ISSUER=my-api
JWT_AUDIENCE=my-api

# JWT Signing
JWT_ALGORITHM=HS256
JWT_SIGNING_KEY=your-secret-key

# Rate Limits
API_CLIENT_TOKEN_RATE=10/minute
API_CLIENT_REFRESH_RATE=30/minute
PER_CLIENT_DEFAULT_RATE=1000/hour
```

---

## Troubleshooting

### "Invalid client credentials"

- **Cause:** Incorrect client_id or client_secret
- **Solution:** Verify credentials are correct. Create a new API client if needed.

### "API client is disabled"

- **Cause:** Client's `is_active` field is False
- **Solution:** Re-enable the client:
  ```python
  api_client.enable()
  ```

### "Token has been revoked"

- **Cause:** Token version mismatch (tokens were revoked)
- **Solution:** Obtain new tokens using client credentials

### "Access denied from this IP address"

- **Cause:** Request IP not in `allowed_ips`
- **Solution:** Add IP to whitelist or remove IP restrictions

### Rate limit exceeded

- **Cause:** Too many requests
- **Solution:** Wait for rate limit to reset or request higher limit

---

## Best Practices

1. **Store Secrets Securely** - Use environment variables or secret managers
2. **Rotate Credentials** - Periodically create new API clients and disable old ones
3. **Use HTTPS** - Always use HTTPS in production
4. **Monitor Logs** - Check `APIClientUsageLog` for suspicious activity
5. **Principle of Least Privilege** - Grant minimal required roles/scopes
6. **Set Rate Limits** - Configure appropriate rate limits per client
7. **Use IP Whitelisting** - Restrict access to known IPs when possible
8. **Token Rotation** - Refresh tokens regularly
9. **Audit Regularly** - Review active API clients periodically

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|------------|
| `/api/v1/auth/api-client/token/` | POST | Obtain JWT tokens | 10/min |
| `/api/v1/auth/api-client/token/refresh/` | POST | Refresh access token | 30/min |

---

## Support

For issues or questions:
1. Check the Django logs: `logs/django.log`
2. Review `APIClientUsageLog` for failed attempts
3. Verify settings in `config/settings.py`

---

**Last Updated:** January 2026  
**Django Version:** 5.0.1  
**DRF Version:** 3.14.0  
**SimpleJWT Version:** 5.3.1
