# API Client Quick Reference

## Create API Client

```bash
python manage.py create_api_client \
  --name "My Service" \
  --tenant "acme-corp" \
  --roles "read,write" \
  --scopes "read:projects,write:projects"
```

Save the `client_id` and `client_secret` securely!

---

## Get Access Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
  }'
```

Response:
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "token_type": "Bearer"
}
```

---

## Make Authenticated Request

```bash
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/api-client/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## Python Example

```python
import requests

# Authenticate
response = requests.post(
    'http://localhost:8000/api/v1/auth/api-client/token/',
    json={'client_id': 'YOUR_CLIENT_ID', 'client_secret': 'YOUR_SECRET'}
)
tokens = response.json()

# Make request
headers = {'Authorization': f"Bearer {tokens['access']}"}
projects = requests.get(
    'http://localhost:8000/api/v1/projects/',
    headers=headers
).json()
```

---

## Manage API Clients (Python)

```python
from apps.authentication.models import APIClient

# Get client
client = APIClient.objects.get(client_id='client_abc123')

# Disable client (revokes all tokens)
client.disable()

# Re-enable client
client.enable()

# Revoke all tokens (keeps client active)
client.revoke_tokens()

# Check roles/scopes
if client.has_role('admin'):
    print("Client is admin")

if client.has_scope('write:projects'):
    print("Client can write projects")
```

---

## Permission Classes

```python
from rest_framework.views import APIView
from apps.authentication.permissions import (
    IsAPIClient,
    HasAPIClientRole,
    HasAPIClientScope
)

class MyView(APIView):
    permission_classes = [IsAPIClient, HasAPIClientScope]
    required_scopes = ['read:projects']
    
    def get(self, request):
        # Access request.api_client
        # Access request.tenant
        return Response(...)
```

---

## Token Claims

Access token includes:
- `client_id` - API client ID
- `tenant_id` - Tenant UUID
- `tenant_slug` - Tenant slug
- `roles` - List of roles
- `scopes` - List of scopes
- `token_version` - For revocation
- `iss`, `aud`, `sub`, `exp`, `iat`, `jti` - Standard JWT claims

---

## Default Settings

- Access token lifetime: **15 minutes**
- Refresh token lifetime: **7 days**
- Token rate limit: **10/minute**
- Refresh rate limit: **30/minute**
- Default client rate limit: **1000/hour**

---

## Troubleshooting

**"Invalid client credentials"** → Check client_id and client_secret

**"API client is disabled"** → Run `client.enable()`

**"Token has been revoked"** → Get new tokens with credentials

**Rate limit exceeded** → Wait or increase limit

---

See [API_CLIENT_AUTH.md](./API_CLIENT_AUTH.md) for complete documentation.
