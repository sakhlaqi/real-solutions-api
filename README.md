# Multi-Tenant Django API Service

A production-grade Django backend service that operates strictly as an API-only, multi-tenant data layer with JWT-based authentication, API client support, and strict tenant isolation.

## 🎯 Overview

This service provides:
- **API-Only Architecture**: No UI, templates, or server-side rendering
- **Multi-Tenant Support**: Shared infrastructure with strict data isolation
- **JWT Authentication**: Token-based authentication with tenant identification
- **API Client Authentication**: Machine-to-machine authentication using client_id + client_secret
- **Tenant Isolation**: Automatic tenant scoping at all layers (ORM, views, middleware)
- **Production-Ready**: Comprehensive security, logging, and error handling

## 🔑 Authentication Methods

### 1. User Authentication (Username + Password)
Traditional user authentication with JWT tokens:
- Endpoint: `POST /api/v1/auth/token/`
- Returns: JWT access + refresh tokens with tenant claims

### 2. API Client Authentication (Client ID + Secret) **NEW!**
Machine-to-machine authentication for service accounts:
- Endpoint: `POST /api/v1/auth/api-client/token/`
- Returns: JWT access + refresh tokens with tenant, roles, and scopes
- **See [API_CLIENT_AUTH.md](./API_CLIENT_AUTH.md) for complete guide**

## 🏗️ Architecture

### Key Components

1. **Tenant Resolution**: Extracted from JWT token (`tenant` claim)
2. **Authentication Layer**: Custom JWT authentication with tenant validation
3. **API Client System**: Secure client credentials with hashed secrets
4. **Middleware**: Automatic tenant context injection into requests
5. **ORM Layer**: Tenant-scoped managers and querysets
6. **API Layer**: Tenant-filtered views and serializers

### Request Lifecycle

```
1. Client Request with JWT Token
   ↓
2. TenantJWTAuthentication or APIClientJWTAuthentication validates token
   ↓
3. Extracts 'tenant' claim from JWT
   ↓
4. Resolves Tenant object from database
   ↓
5. Attaches request.tenant (and request.api_client for API clients)
   ↓
6. TenantMiddleware validates tenant is active
   ↓
7. Views automatically filter data by request.tenant
   ↓
8. Serializers validate cross-tenant references
   ↓
9. Response sent (tenant-scoped data only)
```

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 13+
- pip and virtualenv

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
cd /Users/salmanakhlaqi/Public/projects/real-solutions/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# IMPORTANT: Change SECRET_KEY and JWT_SIGNING_KEY in production!
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb real_solutions

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
```

### 4. Create Test Data

```bash
# Generate sample tenants, users, and test tokens
python manage.py create_test_data

# This creates test_tokens.json with JWT tokens for testing
```

### 4b. Create API Client (Optional)

```bash
# Create an API client for machine-to-machine authentication
python manage.py create_api_client \
  --name "My Service" \
  --tenant "acme" \
  --roles "read,write" \
  --scopes "read:projects,write:projects"

# Save the client_id and client_secret shown in the output!
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

### Access API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Authentication

All API endpoints require JWT authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

**Two Authentication Methods Available:**

1. **User Authentication** - For human users and interactive applications
2. **API Client Authentication** - For services, automation, and machine-to-machine communication

See [AUTHENTICATION_METHODS.md](./AUTHENTICATION_METHODS.md) for detailed comparison and usage.

### Available Endpoints

#### Authentication

**User Authentication (Username + Password):**
- `POST /api/v1/auth/token/` - Obtain JWT token with username/password
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `POST /api/v1/auth/token/verify/` - Verify JWT token

**API Client Authentication (Client ID + Secret):**
- `POST /api/v1/auth/api-client/token/` - Obtain JWT token with client credentials
- `POST /api/v1/auth/api-client/token/refresh/` - Refresh API client token

#### Projects
- `GET /api/v1/projects/` - List all projects (tenant-scoped)
- `POST /api/v1/projects/` - Create a new project
- `GET /api/v1/projects/{id}/` - Retrieve a project
- `PUT /api/v1/projects/{id}/` - Update a project
- `PATCH /api/v1/projects/{id}/` - Partial update
- `DELETE /api/v1/projects/{id}/` - Delete a project
- `GET /api/v1/projects/{id}/tasks/` - List project tasks
- `GET /api/v1/projects/statistics/` - Get project statistics

#### Tasks
- `GET /api/v1/tasks/` - List all tasks (tenant-scoped)
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{id}/` - Retrieve a task
- `PUT /api/v1/tasks/{id}/` - Update a task
- `PATCH /api/v1/tasks/{id}/` - Partial update
- `DELETE /api/v1/tasks/{id}/` - Delete a task
- `GET /api/v1/tasks/by-status/?status=todo` - Filter by status
- `POST /api/v1/tasks/{id}/complete/` - Mark as complete

#### Documents
- `GET /api/v1/documents/` - List all documents (tenant-scoped)
- `POST /api/v1/documents/` - Create a new document
- `GET /api/v1/documents/{id}/` - Retrieve a document
- `PUT /api/v1/documents/{id}/` - Update a document
- `DELETE /api/v1/documents/{id}/` - Delete a document
- `GET /api/v1/documents/?project={id}` - Filter by project

## 🔐 JWT Token Structure

### Required Claims

```json
{
  "user_id": 1,
  "tenant": "uuid-of-tenant",
  "exp": 1234567890,
  "iat": 1234567890,
  "iss": "multitenant-api",
  "aud": "multitenant-api",
  "jti": "unique-token-id",
  "token_type": "access"
}
```

The `tenant` claim is **required** and must reference a valid, active tenant UUID.

## 🧪 Testing the API

### Using cURL (User Authentication)

```bash
# Load test tokens
TOKEN=$(cat test_tokens.json | jq -r '.tenants[0].access_token')

# List projects
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/

# Create a project
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"New Project","description":"Test project","status":"active"}' \
     http://localhost:8000/api/v1/projects/

# Get project statistics
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/statistics/
```

### Using cURL (API Client Authentication)

```bash
# Get API client token
RESPONSE=$(curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \
  -H "Content-Type: application/json" \
  -d '{"client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_SECRET"}')

TOKEN=$(echo $RESPONSE | jq -r '.access')

# Use the token
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/
```

### Using Python

```python
import requests
import json

# Load test token
with open('test_tokens.json') as f:
    data = json.load(f)
    token = data['tenants'][0]['access_token']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# List projects
response = requests.get(
    'http://localhost:8000/api/v1/projects/',
    headers=headers
)
print(response.json())

# Create a task
task_data = {
    'project': 1,  # Use actual project ID
    'title': 'New Task',
    'description': 'Task description',
    'status': 'todo',
    'priority': 'medium'
}
response = requests.post(
    'http://localhost:8000/api/v1/tasks/',
    headers=headers,
    json=task_data
)
print(response.json())
```

## 🛡️ Security Features

### Tenant Isolation Guarantees

1. **Token-Based Identification**: Tenant ID extracted only from JWT
2. **Automatic Query Filtering**: All ORM queries scoped to tenant
3. **Middleware Validation**: Tenant validated before business logic
4. **Serializer Validation**: Cross-tenant references rejected
5. **Model-Level Safeguards**: Foreign key validation enforced

### Cross-Tenant Access Prevention

The system prevents cross-tenant data access through multiple layers:

1. **Authentication Layer**: Validates tenant in JWT token
2. **Middleware Layer**: Attaches and validates tenant context
3. **View Layer**: Filters querysets by `request.tenant`
4. **Serializer Layer**: Validates related objects belong to same tenant
5. **Model Layer**: Enforces tenant consistency on save

### Example: What Happens if You Try to Access Another Tenant's Data?

```python
# Tenant A's token is used
# Trying to access Tenant B's project with ID from another tenant

GET /api/v1/projects/tenant-b-project-id/
Authorization: Bearer <tenant-a-token>

# Response: 404 Not Found
# The project is filtered out by the tenant-scoped queryset
```

## 📁 Project Structure

```
api/
├── config/                      # Django configuration
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
├── apps/
│   ├── tenants/                # Tenant management
│   │   ├── models.py           # Tenant model & TenantAwareModel base
│   │   ├── managers.py         # Tenant-scoped managers
│   │   ├── middleware.py       # Tenant resolution middleware
│   │   └── admin.py            # Admin interface
│   ├── authentication/         # JWT authentication
│   │   ├── models.py           # APIClient & APIClientUsageLog
│   │   ├── authentication.py   # TenantJWTAuthentication & APIClientJWTAuthentication
│   │   ├── permissions.py      # Custom permissions (IsAPIClient, HasAPIClientRole, etc.)
│   │   ├── serializers.py      # Token serializers
│   │   ├── tokens.py           # Custom JWT token classes
│   │   ├── throttling.py       # Rate limiting
│   │   ├── views.py            # Token endpoints
│   │   ├── admin.py            # Admin interface for API clients
│   │   ├── utils.py            # Token generation utilities
│   │   ├── urls.py             # Auth endpoints
│   │   └── management/
│   │       └── commands/
│   │           └── create_api_client.py  # API client creation
│   └── core/                   # Core business logic
│       ├── models.py           # Example models (Project, Task, Document)
│       ├── serializers.py      # DRF serializers
│       ├── views.py            # API views with tenant filtering
│       ├── urls.py             # API endpoints
│       ├── exceptions.py       # Custom exceptions
│       └── management/         # Management commands
│           └── commands/
│               └── create_test_data.py
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── AUTHENTICATION_METHODS.md   # Comparison of auth methods
├── API_CLIENT_AUTH.md          # Complete API client guide
├── API_CLIENT_QUICKSTART.md    # Quick reference for API clients
├── MIGRATION_GUIDE.md          # Migration guide for deployments
└── IMPLEMENTATION_SUMMARY.md   # Technical implementation details
```

## 🔧 Development Guide

### Creating Tenant-Aware Models

```python
from apps.tenants.models import TenantAwareModel
from apps.tenants.managers import TenantManager

class YourModel(TenantAwareModel):
    """Your model inherits tenant field and timestamps."""
    
    name = models.CharField(max_length=255)
    
    # Use the tenant-aware manager
    objects = TenantManager()
    
    class Meta:
        db_table = 'your_models'
        indexes = [
            models.Index(fields=['tenant', 'name']),
        ]
```

### Creating Tenant-Scoped Views

```python
from apps.core.views import TenantScopedViewSetMixin
from rest_framework import viewsets

class YourViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """Automatically filters by tenant."""
    
    queryset = YourModel.objects.all()
    serializer_class = YourSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
```

### Querying Tenant Data

```python
# In views with request.tenant available
projects = Project.objects.for_tenant(request.tenant).filter(status='active')

# Creating objects
project = Project.objects.create_for_tenant(
    request.tenant,
    name='New Project',
    description='Description'
)
```

### Generating JWT Tokens Programmatically

```python
from apps.authentication.utils import generate_tenant_token

# Generate token for a user and tenant
tokens = generate_tenant_token(user, tenant)
access_token = tokens['access']
refresh_token = tokens['refresh']
```

## 🚀 Production Deployment

### Environment Variables (Production)

```bash
# Security - CHANGE THESE!
SECRET_KEY=your-production-secret-key-min-50-chars
JWT_SIGNING_KEY=your-jwt-signing-key-min-50-chars

# Database
DB_NAME=your_production_db
DB_USER=your_db_user
DB_PASSWORD=strong_password
DB_HOST=your-db-host.com
DB_PORT=5432

# Environment
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com,yourdomain.com

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15  # Shorter in production
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_ALGORITHM=RS256  # Consider RS256 with key pairs
JWT_ISSUER=your-api-domain
JWT_AUDIENCE=your-api-domain

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Using Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 📊 Monitoring & Logging

### Logs

Logs are written to:
- Console (stdout/stderr)
- `logs/django.log` (errors only)

Log entries include tenant context:
```
INFO 2026-01-12 10:30:45 [tenant:acme] User authenticated successfully
ERROR 2026-01-12 10:35:22 [tenant:beta] Database query failed
```

### Health Check Endpoint

Add a health check view for monitoring:

```python
# In apps/core/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'healthy'})
```

## 🔍 Troubleshooting

### Common Issues

**Issue**: "Tenant not found or inactive"
- **Solution**: Ensure JWT token contains valid `tenant` claim
- **Check**: Token was generated with correct tenant ID

**Issue**: "Project does not belong to your tenant"
- **Solution**: Verify you're not trying to reference another tenant's resources
- **Check**: All foreign keys point to objects within the same tenant

**Issue**: Database connection errors
- **Solution**: Check PostgreSQL is running and credentials are correct
- **Check**: `.env` file has correct database configuration

## 🧩 Advanced Features

### Service-to-Service Authentication

```python
from apps.authentication.utils import generate_service_token

# Generate service token
token = generate_service_token(
    tenant=tenant_instance,
    service_name='payment-service',
    expiration_minutes=60
)

# Use ServiceToServiceAuthentication in views
from apps.authentication.authentication import ServiceToServiceAuthentication

class ServiceOnlyView(APIView):
    authentication_classes = [ServiceToServiceAuthentication]
    permission_classes = [IsServiceAccount]
```

### Per-Tenant Rate Limiting

Implement custom throttle class:

```python
from rest_framework.throttling import UserRateThrottle

class TenantRateThrottle(UserRateThrottle):
    def get_cache_key(self, request, view):
        if hasattr(request, 'tenant'):
            ident = f"{request.tenant.id}_{request.user.id}"
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}
```

## 📄 License

[Your License Here]

## 👥 Contributing

[Your Contributing Guidelines]

## 📞 Support

For issues or questions, please contact [your-contact-info]

---

**Built with Django, DRF, and PostgreSQL** • **Production-Ready Multi-Tenant API**
