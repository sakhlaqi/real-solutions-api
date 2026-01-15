# CORS Configuration Guide

## Overview

The API supports Cross-Origin Resource Sharing (CORS) with flexible configuration for multi-tenant subdomain access across different environments.

## Configuration Structure

### 1. Explicit Origins (`CORS_ALLOWED_ORIGINS`)

Specified in the `.env` file for exact domain matches:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

These origins are matched exactly and are typically used for:
- Specific localhost ports during development
- Admin/management interfaces
- Non-tenant specific endpoints

### 2. Pattern-Based Origins (`CORS_ALLOWED_ORIGIN_REGEXES`)

Dynamic pattern matching for tenant subdomains across environments.

## Environment-Specific Patterns

### Local Development (`DEBUG=True`)

Automatically supports:
- `http://*.localhost:3000` - HTTP subdomain access
- `https://*.localhost:3000` - HTTPS subdomain access

**Examples:**
- `http://acme.localhost:3000`
- `http://demo.localhost:3000`
- `https://tenant1.localhost:3000`

**Access Methods:**
1. **Subdomain approach** (recommended):
   - `http://acme.localhost:3000`
   
2. **Query parameter fallback**:
   - `http://localhost:3000?tenant=acme`

### Production Environment (`DEBUG=False`, `APP_ENV=production`)

Pattern: `https://*.{BASE_DOMAIN}`

**Configuration:**
```env
DEBUG=False
APP_ENV=production
BASE_DOMAIN=yourdomain.com
ALLOWED_HOSTS=.yourdomain.com,yourdomain.com
```

**Matches:**
- `https://acme.yourdomain.com`
- `https://demo.yourdomain.com`
- `https://tenant1.yourdomain.com`

### Staging Environment (`DEBUG=False`, `APP_ENV=staging`)

Patterns:
1. `https://*.{BASE_DOMAIN}` (main production-like)
2. `https://*.staging.{BASE_DOMAIN}` (staging-specific)

**Configuration:**
```env
DEBUG=False
APP_ENV=staging
BASE_DOMAIN=yourdomain.com
ALLOWED_HOSTS=.staging.yourdomain.com,staging.yourdomain.com,.yourdomain.com
```

**Matches:**
- `https://acme.staging.yourdomain.com`
- `https://demo.staging.yourdomain.com`
- `https://acme.yourdomain.com` (for testing prod-like URLs)

### Development Environment (Remote) (`DEBUG=False`, `APP_ENV=development`)

Patterns:
1. `https://*.{BASE_DOMAIN}` (main)
2. `https://*.dev.{BASE_DOMAIN}` (dev-specific)
3. `http://*.dev.{BASE_DOMAIN}` (HTTP for internal networks)

**Configuration:**
```env
DEBUG=False
APP_ENV=development
BASE_DOMAIN=yourdomain.com
ALLOWED_HOSTS=.dev.yourdomain.com,dev.yourdomain.com,.yourdomain.com
```

**Matches:**
- `https://acme.dev.yourdomain.com`
- `http://acme.dev.yourdomain.com` (non-SSL development)
- `https://acme.yourdomain.com` (testing prod URLs)

## Implementation Details

### settings.py

```python
# Base patterns (always active)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://[a-z0-9-]+\.localhost(:\d+)?$",
    r"^https://[a-z0-9-]+\.localhost(:\d+)?$",
]

# Environment-specific patterns (when DEBUG=False)
if not DEBUG:
    BASE_DOMAIN = config('BASE_DOMAIN', default='yourdomain.com')
    
    # Main domain pattern (all environments)
    CORS_ALLOWED_ORIGIN_REGEXES.append(
        rf"^https://[a-z0-9-]+\.{BASE_DOMAIN.replace('.', r'\.')}$"
    )
    
    APP_ENV = config('APP_ENV', default='development')
    
    # Staging-specific
    if APP_ENV == 'staging':
        CORS_ALLOWED_ORIGIN_REGEXES.append(
            rf"^https://[a-z0-9-]+\.staging\.{BASE_DOMAIN.replace('.', r'\.')}$"
        )
    
    # Development-specific (remote dev server)
    elif APP_ENV == 'development':
        CORS_ALLOWED_ORIGIN_REGEXES.extend([
            rf"^https://[a-z0-9-]+\.dev\.{BASE_DOMAIN.replace('.', r'\.')}$",
            rf"^http://[a-z0-9-]+\.dev\.{BASE_DOMAIN.replace('.', r'\.')}$"
        ])
```

### Allowed Hosts

Must be configured to accept wildcard subdomains:

**Local:**
```env
ALLOWED_HOSTS=localhost,127.0.0.1,.localhost
```

**Production:**
```env
ALLOWED_HOSTS=.yourdomain.com,yourdomain.com
```

**Staging:**
```env
ALLOWED_HOSTS=.staging.yourdomain.com,staging.yourdomain.com
```

**Development (Remote):**
```env
ALLOWED_HOSTS=.dev.yourdomain.com,dev.yourdomain.com
```

## Tenant Slug Pattern

All regex patterns match tenant slugs with the following constraints:
- **Pattern:** `[a-z0-9-]+`
- **Characters:** Lowercase letters, numbers, hyphens
- **Length:** 2-63 characters
- **Format:** Must start and end with alphanumeric (not hyphen)

**Valid tenant slugs:**
- `acme`
- `demo`
- `tenant-1`
- `my-company-2024`

**Invalid tenant slugs:**
- `-acme` (starts with hyphen)
- `acme-` (ends with hyphen)
- `ACME` (uppercase)
- `acme_corp` (underscore)

## Security Considerations

1. **Credentials:** `CORS_ALLOW_CREDENTIALS = True` allows cookies/auth headers
2. **HTTPS Only:** Production enforces HTTPS via security middleware
3. **Exact Matching:** Regex patterns prevent subdomain hijacking
4. **No Wildcards in Production:** All origins explicitly defined or pattern-matched

## Testing CORS

### Local Development

```bash
# Test with subdomain
curl -i -X OPTIONS \
  -H "Origin: http://acme.localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  http://localhost:8000/api/v1/tenants/acme/config/

# Expected headers:
# Access-Control-Allow-Origin: http://acme.localhost:3000
# Access-Control-Allow-Credentials: true
```

### Production

```bash
# Test production CORS
curl -i -X OPTIONS \
  -H "Origin: https://acme.yourdomain.com" \
  -H "Access-Control-Request-Method: GET" \
  https://api.yourdomain.com/api/v1/tenants/acme/config/
```

## Troubleshooting

### Issue: CORS error on subdomain

**Check:**
1. Django server restarted after `.env` changes
2. `ALLOWED_HOSTS` includes wildcard: `.localhost` or `.yourdomain.com`
3. `BASE_DOMAIN` set correctly in `.env`
4. Origin matches regex pattern (check browser console)

### Issue: localhost subdomain not resolving

**Solutions:**
1. Modern browsers support `*.localhost` natively
2. Add to `/etc/hosts` if needed:
   ```
   127.0.0.1 acme.localhost
   127.0.0.1 demo.localhost
   ```
3. Use query parameter fallback: `?tenant=acme`

### Issue: Production CORS working but staging/dev not

**Check:**
- `APP_ENV` environment variable is set correctly
- `DEBUG=False` in non-local environments
- Regex patterns are being added (check Django startup logs)

## Environment File Examples

### Local Development (.env)
```env
DEBUG=True
APP_ENV=development
ALLOWED_HOSTS=localhost,127.0.0.1,.localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
BASE_DOMAIN=yourdomain.com
```

### Staging (.env.staging)
```env
DEBUG=False
APP_ENV=staging
ALLOWED_HOSTS=.staging.yourdomain.com,staging.yourdomain.com
CORS_ALLOWED_ORIGINS=https://admin.staging.yourdomain.com
BASE_DOMAIN=yourdomain.com
SECRET_KEY=your-staging-secret-key
```

### Production (.env.production)
```env
DEBUG=False
APP_ENV=production
ALLOWED_HOSTS=.yourdomain.com,yourdomain.com
CORS_ALLOWED_ORIGINS=https://admin.yourdomain.com
BASE_DOMAIN=yourdomain.com
SECRET_KEY=your-production-secret-key
```

## Related Configuration

- Tenant resolution: `apps/tenants/middleware.py`
- Frontend tenant resolver: `presentation/src/services/tenantResolver.ts`
- Authentication: JWT tokens include tenant claims
- Database isolation: Tenant-aware models and querysets
