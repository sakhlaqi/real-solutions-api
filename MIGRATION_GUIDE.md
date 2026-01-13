# Migration Guide - Adding API Client Authentication

This guide helps you add API client authentication to an existing deployment.

---

## Pre-Migration Checklist

- [ ] Backup your database
- [ ] Review current authentication configuration
- [ ] Identify services that will use API clients
- [ ] Plan credential distribution strategy
- [ ] Schedule maintenance window if needed

---

## Step 1: Update Dependencies

The implementation uses existing dependencies. Verify they're installed:

```bash
pip install -r requirements.txt
```

Required packages (already in requirements.txt):
- Django==5.0.1
- djangorestframework==3.14.0
- djangorestframework-simplejwt==5.3.1
- PyJWT==2.8.0
- cryptography==42.0.0

---

## Step 2: Run Database Migrations

Apply the new migrations to create API client tables:

```bash
python manage.py migrate authentication
```

This creates:
- `api_clients` table
- `api_client_usage_logs` table
- Associated indexes

---

## Step 3: Update Settings (Already Done)

The settings have been updated with:
- `APIClientJWTAuthentication` in `DEFAULT_AUTHENTICATION_CLASSES`
- Rate limit configurations
- JWT token lifetime adjustments (15 min access, 7 day refresh)

**⚠️ Important:** Access token lifetime changed from 60 minutes to 15 minutes for better security.

### Environment Variables

Add these to your `.env` file:

```bash
# JWT Token Lifetimes
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Rate Limits
API_CLIENT_TOKEN_RATE=10/minute
API_CLIENT_REFRESH_RATE=30/minute
PER_CLIENT_DEFAULT_RATE=1000/hour
```

---

## Step 4: Create API Clients

### For Each Service Needing M2M Access:

```bash
python manage.py create_api_client \
  --name "Service Name" \
  --tenant "tenant-slug" \
  --description "Purpose of this client" \
  --roles "read,write" \
  --scopes "read:projects,write:projects" \
  --rate-limit 5000
```

**⚠️ Security:** Save the client_secret immediately. It's shown only once!

### Example for a Data Sync Service:

```bash
python manage.py create_api_client \
  --name "Data Sync Service" \
  --tenant "acme-corp" \
  --description "Automated data synchronization service" \
  --roles "read,write" \
  --scopes "read:projects,write:projects,read:tasks,write:tasks" \
  --rate-limit 10000
```

### Example for a Monitoring Service:

```bash
python manage.py create_api_client \
  --name "Monitoring Service" \
  --tenant "acme-corp" \
  --description "Health checks and monitoring" \
  --roles "read" \
  --scopes "read:health,read:metrics" \
  --rate-limit 1000
```

### With IP Whitelisting:

```bash
python manage.py create_api_client \
  --name "Internal Service" \
  --tenant "acme-corp" \
  --allowed-ips "10.0.1.5,10.0.1.6,192.168.1.100" \
  --roles "admin" \
  --scopes "read:*,write:*,delete:*"
```

---

## Step 5: Update Client Applications

### Replace Basic Auth with API Client Auth

**Before (Username/Password):**
```python
response = requests.post('http://api.example.com/api/v1/auth/token/', json={
    'username': 'service_user',
    'password': 'password123',
    'tenant': 'acme-corp'
})
```

**After (Client Credentials):**
```python
response = requests.post('http://api.example.com/api/v1/auth/api-client/token/', json={
    'client_id': 'client_a1b2c3d4e5f6',
    'client_secret': 'XyZ123AbC456DeF789...'
})
```

### Sample Client Code

```python
import requests
from datetime import datetime, timedelta

class APIClient:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def authenticate(self):
        """Obtain initial tokens."""
        response = requests.post(
            f'{self.base_url}/api/v1/auth/api-client/token/',
            json={
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data['access']
        self.refresh_token = data['refresh']
        self.token_expires_at = datetime.fromtimestamp(data['access_token_expires_at'])
    
    def refresh_access_token(self):
        """Refresh the access token."""
        response = requests.post(
            f'{self.base_url}/api/v1/auth/api-client/token/refresh/',
            json={'refresh': self.refresh_token}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data['access']
        self.token_expires_at = datetime.fromtimestamp(data['access_token_expires_at'])
    
    def ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if not self.access_token:
            self.authenticate()
        elif datetime.now() >= self.token_expires_at - timedelta(minutes=1):
            self.refresh_access_token()
    
    def request(self, method, path, **kwargs):
        """Make an authenticated request."""
        self.ensure_authenticated()
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        kwargs['headers'] = headers
        
        response = requests.request(method, f'{self.base_url}{path}', **kwargs)
        return response

# Usage
client = APIClient(
    base_url='http://api.example.com',
    client_id='client_a1b2c3d4e5f6',
    client_secret='XyZ123AbC456DeF789...'
)

# Make requests
projects = client.request('GET', '/api/v1/projects/').json()
```

---

## Step 6: Configure Existing Views (Optional)

### Add Role/Scope Enforcement

Update views to require specific roles or scopes:

```python
from rest_framework.views import APIView
from apps.authentication.permissions import IsAPIClient, HasAPIClientScope

class ProjectListView(APIView):
    permission_classes = [IsAPIClient, HasAPIClientScope]
    required_scopes = ['read:projects']
    
    def get(self, request):
        # Only API clients with 'read:projects' can access
        projects = Project.objects.filter(tenant=request.tenant)
        return Response(...)
```

### Allow Both User and API Client Authentication

```python
from apps.authentication.permissions import IsAPIClientOrUser

class ProjectDetailView(APIView):
    permission_classes = [IsAPIClientOrUser]
    
    def get(self, request, pk):
        # Both regular users and API clients can access
        if hasattr(request, 'api_client'):
            # Request from API client
            client = request.api_client
        else:
            # Request from regular user
            user = request.user
        
        project = Project.objects.get(pk=pk, tenant=request.tenant)
        return Response(...)
```

---

## Step 7: Update API Documentation

Update your API documentation to include:
- New authentication endpoints
- API client authentication flow
- Rate limits
- Example requests

Swagger/OpenAPI will automatically include the new endpoints.

---

## Step 8: Monitor and Test

### Test the New Endpoints

```bash
# Test token issuance
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{"client_id":"...","client_secret":"..."}'

# Test authenticated request
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer <access_token>"
```

### Monitor Usage Logs

Check Django admin → API Client Usage Logs for:
- Failed authentication attempts
- Unusual IP addresses
- High-frequency requests

```python
from apps.authentication.models import APIClientUsageLog

# Failed attempts in last hour
recent_failures = APIClientUsageLog.objects.filter(
    success=False,
    timestamp__gte=timezone.now() - timedelta(hours=1)
)
```

---

## Step 9: Secure Credential Storage

### Store Credentials Securely

**✅ DO:**
- Use environment variables
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)
- Encrypt credentials at rest
- Rotate credentials periodically

**❌ DON'T:**
- Commit credentials to version control
- Store in plain text configuration files
- Share credentials via email or chat
- Use the same credentials across environments

### Example with Environment Variables

```bash
# .env (never commit this!)
API_CLIENT_ID=client_a1b2c3d4e5f6
API_CLIENT_SECRET=XyZ123AbC456DeF789...
```

```python
import os
from decouple import config

client_id = config('API_CLIENT_ID')
client_secret = config('API_CLIENT_SECRET')
```

---

## Step 10: Rollback Plan (If Needed)

If you need to rollback:

1. **Disable API clients:**
   ```python
   from apps.authentication.models import APIClient
   APIClient.objects.all().update(is_active=False)
   ```

2. **Remove from settings:**
   ```python
   # In config/settings.py
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'apps.authentication.authentication.TenantJWTAuthentication',
           # Remove: 'apps.authentication.authentication.APIClientJWTAuthentication',
       ],
   }
   ```

3. **Revert migrations (if necessary):**
   ```bash
   python manage.py migrate authentication zero
   ```

---

## Post-Migration Tasks

- [ ] Document all API clients and their purposes
- [ ] Set up monitoring alerts for failed auth attempts
- [ ] Schedule credential rotation policy
- [ ] Train team on API client management
- [ ] Review and update access control policies
- [ ] Test disaster recovery procedures

---

## Common Issues and Solutions

### Issue: "Invalid client credentials"
**Solution:** Verify client_id and client_secret are correct. Check if client is active.

### Issue: Rate limit exceeded
**Solution:** Increase rate limit for the client or optimize request frequency.

### Issue: "Token has been revoked"
**Solution:** Token version was incremented. Obtain new tokens with client credentials.

### Issue: IP address blocked
**Solution:** Add IP to allowed_ips or remove IP whitelist restriction.

---

## Support Checklist

Before going live:
- [ ] All API clients created and tested
- [ ] Credentials securely stored
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team trained
- [ ] Rollback plan documented
- [ ] Emergency contacts identified

---

## Need Help?

- Check logs: `logs/django.log`
- Review usage logs: Django admin → API Client Usage Logs
- Run test script: `python test_api_client_auth.py`
- See documentation: `API_CLIENT_AUTH.md`

---

**Migration complete! Your API now supports secure machine-to-machine authentication. 🎉**
