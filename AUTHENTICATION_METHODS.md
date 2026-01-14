# Authentication Methods

This API supports two authentication methods, each designed for different use cases.

---

## 1. User Authentication (Username + Password)

### Purpose
For **human users** accessing the API through interactive applications.

### Endpoint
```
POST /api/v1/auth/token/
```

### Request Body
```json
{
  "username": "user@example.com",
  "password": "user_password",
  "tenant": "tenant-slug"
}
```

### Response
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_expires_at": 1234567890,
  "refresh_expires_at": 1234567890
}
```

### Token Claims
- `user_id` - Django user ID
- `username` - User's username
- `email` - User's email
- `tenant_id` - Tenant UUID
- `tenant_slug` - Tenant slug
- Standard JWT claims: `iss`, `aud`, `sub`, `exp`, `iat`, `jti`

### Use Cases
✅ Frontend web applications (React, Vue, Angular)  
✅ Mobile applications (iOS, Android)  
✅ Admin dashboards  
✅ End-user access  
✅ Personal accounts with user-specific permissions  

### Authentication Class
```python
'apps.authentication.authentication.TenantJWTAuthentication'
```

### Creating Users
```bash
# Create a Django user (via Django admin or shell)
python manage.py createsuperuser

# Or programmatically
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user(
    username='john@example.com',
    password='secure_password',
    email='john@example.com'
)
```

---

## 2. API Client Authentication (Client ID + Secret)

### Purpose
For **machine-to-machine** communication and service accounts.

### Endpoint
```
POST /api/v1/auth/api-client/token/
```

### Request Body
```json
{
  "client_id": "client_a1b2c3d4e5f6",
  "client_secret": "XyZ123AbC456DeF789..."
}
```

### Response
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_token_expires_at": 1234567890,
  "refresh_token_expires_at": 1234567890,
  "token_type": "Bearer"
}
```

### Token Claims
- `client_id` - API client identifier
- `client_type` - "service_account"
- `tenant_id` - Tenant UUID
- `tenant_slug` - Tenant slug
- `roles` - Array of assigned roles
- `scopes` - Array of permissions/scopes
- `token_version` - For revocation support
- Standard JWT claims: `iss`, `aud`, `sub`, `exp`, `iat`, `jti`

### Use Cases
✅ Backend microservices  
✅ Scheduled jobs and cron tasks  
✅ Data synchronization services  
✅ Third-party integrations  
✅ CI/CD pipelines  
✅ Automated testing  
✅ Server-to-server communication  

### Authentication Class
```python
'apps.authentication.authentication.APIClientJWTAuthentication'
```

### Creating API Clients
```bash
python manage.py create_api_client \
  --name "Service Name" \
  --tenant "tenant-slug" \
  --roles "read,write" \
  --scopes "read:projects,write:projects" \
  --rate-limit 5000
```

**⚠️ Important:** Save the `client_secret` immediately - it's shown only once!

---

## Comparison Matrix

| Feature | User Auth | API Client Auth |
|---------|-----------|-----------------|
| **Authentication** | username + password | client_id + client_secret |
| **Target Users** | Humans | Services/Machines |
| **Secret Storage** | Django password hashers | Django password hashers |
| **Token Lifetime** | 15 min access / 7 day refresh | 15 min access / 7 day refresh |
| **Rate Limiting** | 1000/hour (default) | Configurable per client |
| **Roles/Scopes** | User permissions | Assigned roles/scopes |
| **IP Whitelisting** | Not supported | Optional |
| **Audit Logging** | Django auth logs | APIClientUsageLog table |
| **Revocation** | Disable user account | Disable client or increment token_version |
| **Management** | Django admin / User model | Management command / APIClient model |

---

## Token Refresh (Both Methods)

### User Token Refresh
```
POST /api/v1/auth/token/refresh/
```

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### API Client Token Refresh
```
POST /api/v1/auth/api-client/token/refresh/
```

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Making Authenticated Requests (Both Methods)

Once you have an access token from either method, use it the same way:

```bash
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer <access_token>"
```

```python
import requests

headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/api/v1/projects/", headers=headers)
```

---

## Choosing the Right Method

### Use **User Authentication** when:
- Building interactive applications (web/mobile)
- Users need to log in with personal credentials
- You need user-specific permissions and profiles
- Audit trail should show individual users
- Sessions are interactive and user-driven

### Use **API Client Authentication** when:
- Building automated services or integrations
- No human interaction involved
- Service needs to run 24/7 unattended
- You need service-level permissions (not user-specific)
- Credentials should be stored in environment variables or secret managers
- You want to track service usage separately

---

## Security Best Practices

### For User Authentication:
- ✅ Enforce strong password policies
- ✅ Implement account lockout after failed attempts
- ✅ Use HTTPS in production
- ✅ Store user passwords securely (Django handles this)
- ✅ Implement password reset flows
- ✅ Consider MFA for sensitive operations

### For API Client Authentication:
- ✅ Store client secrets in environment variables or secret managers
- ✅ Never commit secrets to version control
- ✅ Use IP whitelisting when possible
- ✅ Set appropriate rate limits per client
- ✅ Rotate credentials periodically
- ✅ Monitor APIClientUsageLog for suspicious activity
- ✅ Use minimal required scopes (principle of least privilege)
- ✅ Disable unused API clients

---

## Example Scenarios

### Scenario 1: Web Application with Background Jobs
```
Frontend (React) → User Auth → Access API
Backend Cron Job → API Client Auth → Access API
```

### Scenario 2: Mobile App with Sync Service
```
Mobile App → User Auth → Access API
Sync Service → API Client Auth → Access API
```

### Scenario 3: Multi-Service Architecture
```
Web Dashboard → User Auth → Access API
Data Pipeline Service → API Client Auth → Access API
Analytics Service → API Client Auth → Access API
Monitoring Service → API Client Auth → Access API
```

---

## Migration Path

If you currently use only user authentication and want to add API client authentication:

1. **Keep existing user authentication** - Don't break existing apps
2. **Create API clients** for services currently using service user accounts
3. **Update services** to use API client credentials instead
4. **Monitor usage** through APIClientUsageLog
5. **Gradually migrate** services from user auth to API client auth
6. **Deprecate service user accounts** once migration is complete

---

## Reference Documentation

- **Complete API Client Guide:** [API_CLIENT_AUTH.md](./API_CLIENT_AUTH.md)
- **Quick Reference:** [API_CLIENT_QUICKSTART.md](./API_CLIENT_QUICKSTART.md)
- **Implementation Summary:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Migration Guide:** [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

---

## Support

### Check Logs
```bash
# Django logs
tail -f logs/django.log

# API client usage logs (Django admin)
http://localhost:8000/admin/authentication/apiclientusagelog/
```

### Test Authentication
```bash
# Test user auth
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"pass","tenant":"tenant-slug"}'

# Test API client auth
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{"client_id":"client_xxx","client_secret":"secret"}'
```

---

**Last Updated:** January 2026
