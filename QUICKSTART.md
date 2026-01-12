# Quick Reference Guide

## Common Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create test data
python manage.py create_test_data
```

### Run Server
```bash
# Development server
python manage.py runserver

# Production with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell
```

---

## API Endpoints Quick Reference

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/token/` | Get access token |
| POST | `/auth/token/refresh/` | Refresh token |
| POST | `/auth/token/verify/` | Verify token |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects/` | List projects |
| POST | `/projects/` | Create project |
| GET | `/projects/{id}/` | Get project |
| PUT/PATCH | `/projects/{id}/` | Update project |
| DELETE | `/projects/{id}/` | Delete project |
| GET | `/projects/{id}/tasks/` | List project tasks |
| GET | `/projects/statistics/` | Get statistics |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/` | List tasks |
| POST | `/tasks/` | Create task |
| GET | `/tasks/{id}/` | Get task |
| PUT/PATCH | `/tasks/{id}/` | Update task |
| DELETE | `/tasks/{id}/` | Delete task |
| GET | `/tasks/by-status/?status=todo` | Filter by status |
| POST | `/tasks/{id}/complete/` | Mark complete |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/documents/` | List documents |
| POST | `/documents/` | Create document |
| GET | `/documents/{id}/` | Get document |
| PUT/PATCH | `/documents/{id}/` | Update document |
| DELETE | `/documents/{id}/` | Delete document |

---

## cURL Quick Examples

```bash
# Get token from test data
TOKEN=$(cat test_tokens.json | jq -r '.tenants[0].access_token')

# List projects
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/

# Create project
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Project","status":"active"}' \
  http://localhost:8000/api/v1/projects/

# Get project
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/1/

# Update project
curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}' \
  http://localhost:8000/api/v1/projects/1/

# Delete project
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/projects/1/
```

---

## Python Quick Examples

```python
import requests

# Get token from test data
import json
with open('test_tokens.json') as f:
    token = json.load(f)['tenants'][0]['access_token']

# Setup headers
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
base_url = 'http://localhost:8000/api/v1'

# List projects
response = requests.get(f'{base_url}/projects/', headers=headers)
projects = response.json()

# Create project
data = {'name': 'Test Project', 'status': 'active'}
response = requests.post(f'{base_url}/projects/', headers=headers, json=data)
project = response.json()

# Get project
response = requests.get(f'{base_url}/projects/{project["id"]}/', headers=headers)

# Update project
data = {'status': 'completed'}
response = requests.patch(f'{base_url}/projects/{project["id"]}/', headers=headers, json=data)

# Delete project
response = requests.delete(f'{base_url}/projects/{project["id"]}/', headers=headers)
```

---

## JWT Token Claims

### Required Claims
- `tenant` - UUID of the tenant (REQUIRED)
- `user_id` - User ID
- `exp` - Expiration timestamp
- `iat` - Issued at timestamp
- `iss` - Issuer (multitenant-api)
- `aud` - Audience (multitenant-api)

### Generating Tokens Programmatically

```python
from apps.authentication.utils import generate_tenant_token
from apps.tenants.models import Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.get(username='acme_user')
tenant = Tenant.objects.get(slug='acme')

tokens = generate_tenant_token(user, tenant)
print(tokens['access'])  # Access token
print(tokens['refresh'])  # Refresh token
```

---

## Environment Variables

### Development (.env)
```bash
SECRET_KEY=dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=real_solutions
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

### Production (.env)
```bash
SECRET_KEY=<generate-secure-50-char-key>
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com

DB_NAME=prod_db
DB_USER=prod_user
DB_PASSWORD=<secure-password>
DB_HOST=db.yourdomain.com
DB_PORT=5432

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_ALGORITHM=RS256
```

---

## Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Inactive tenant |
| 404 | Not Found | Resource doesn't exist (or filtered by tenant) |
| 500 | Server Error | Backend error |

---

## Troubleshooting

### "Tenant not found or inactive"
- Check JWT token contains valid `tenant` claim
- Verify tenant exists and `is_active=True`

### "Project does not belong to your tenant"
- You're trying to reference another tenant's resource
- Check project ID is from your tenant

### Database connection errors
- Verify PostgreSQL is running
- Check `.env` database credentials

### Import errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

---

## File Locations

| Component | Location |
|-----------|----------|
| Settings | `config/settings.py` |
| URLs | `config/urls.py` |
| Tenant Models | `apps/tenants/models.py` |
| Authentication | `apps/authentication/authentication.py` |
| Core Models | `apps/core/models.py` |
| Views | `apps/core/views.py` |
| Serializers | `apps/core/serializers.py` |

---

## API Documentation URLs

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## Security Checklist

### Before Production:
- [ ] Change `SECRET_KEY` in `.env`
- [ ] Change `JWT_SIGNING_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use HTTPS/TLS
- [ ] Set up proper database backups
- [ ] Configure log monitoring
- [ ] Review CORS settings
- [ ] Enable rate limiting
- [ ] Set up firewall rules

---

## Performance Tips

1. **Database Indexes**: Already included on tenant fields
2. **Query Optimization**: Use `select_related()` for foreign keys
3. **Pagination**: Enabled by default (50 items per page)
4. **Caching**: Consider Redis for session/token caching
5. **Read Replicas**: Point read queries to replicas

---

## Next Steps

1. Review [README.md](README.md) for full documentation
2. Check [API_EXAMPLES.md](API_EXAMPLES.md) for detailed examples
3. Read [ARCHITECTURE.md](ARCHITECTURE.md) for isolation details
4. Customize models for your use case
5. Add business logic to views
6. Implement additional endpoints
7. Configure production deployment
