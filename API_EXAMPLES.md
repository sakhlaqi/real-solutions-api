# API Usage Examples

## Table of Contents
1. [Authentication](#authentication)
2. [Projects](#projects)
3. [Tasks](#tasks)
4. [Documents](#documents)
5. [Error Handling](#error-handling)
6. [Advanced Scenarios](#advanced-scenarios)

## Authentication

### Obtain JWT Token

**Request:**
```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "acme_user",
  "password": "testpass123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Note:** The JWT token includes a `tenant` claim. Use test data command to generate tokens with tenant claims.

### Refresh Token

**Request:**
```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Verify Token

**Request:**
```http
POST /api/v1/auth/token/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{}
```
Status: `200 OK` if valid, `401 Unauthorized` if invalid

---

## Projects

### List Projects (Tenant-Scoped)

**Request:**
```http
GET /api/v1/projects/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Website Redesign",
      "description": "Redesign company website with modern UI",
      "status": "active",
      "tasks_count": 2,
      "created_at": "2026-01-12T10:00:00Z",
      "updated_at": "2026-01-12T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Mobile App Development",
      "description": "Build iOS and Android mobile applications",
      "status": "active",
      "tasks_count": 1,
      "created_at": "2026-01-12T10:00:00Z",
      "updated_at": "2026-01-12T10:00:00Z"
    }
  ]
}
```

### Create Project

**Request:**
```http
POST /api/v1/projects/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "E-commerce Platform",
  "description": "Build new e-commerce platform",
  "status": "active"
}
```

**Response:**
```json
{
  "id": 3,
  "name": "E-commerce Platform",
  "description": "Build new e-commerce platform",
  "status": "active",
  "tasks_count": 0,
  "created_at": "2026-01-12T11:00:00Z",
  "updated_at": "2026-01-12T11:00:00Z"
}
```

### Get Project Details

**Request:**
```http
GET /api/v1/projects/1/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Website Redesign",
  "description": "Redesign company website with modern UI",
  "status": "active",
  "tasks_count": 2,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T10:00:00Z"
}
```

### Update Project

**Request:**
```http
PATCH /api/v1/projects/1/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "status": "completed"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Website Redesign",
  "description": "Redesign company website with modern UI",
  "status": "completed",
  "tasks_count": 2,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T11:30:00Z"
}
```

### Get Project Tasks

**Request:**
```http
GET /api/v1/projects/1/tasks/
Authorization: Bearer <your-token>
```

**Response:**
```json
[
  {
    "id": 1,
    "project": 1,
    "project_name": "Website Redesign",
    "title": "Design wireframes",
    "description": "Create wireframes for all pages",
    "status": "done",
    "priority": "high",
    "due_date": null,
    "created_at": "2026-01-12T10:00:00Z",
    "updated_at": "2026-01-12T10:00:00Z"
  },
  {
    "id": 2,
    "project": 1,
    "project_name": "Website Redesign",
    "title": "Implement homepage",
    "description": "Code the new homepage design",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2026-01-20",
    "created_at": "2026-01-12T10:00:00Z",
    "updated_at": "2026-01-12T10:00:00Z"
  }
]
```

### Get Project Statistics

**Request:**
```http
GET /api/v1/projects/statistics/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "total_projects": 3,
  "active_projects": 2,
  "completed_projects": 1,
  "archived_projects": 0,
  "projects_with_tasks": 2
}
```

---

## Tasks

### List Tasks (Tenant-Scoped)

**Request:**
```http
GET /api/v1/tasks/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "project": 1,
      "project_name": "Website Redesign",
      "title": "Design wireframes",
      "description": "Create wireframes for all pages",
      "status": "done",
      "priority": "high",
      "due_date": null,
      "created_at": "2026-01-12T10:00:00Z",
      "updated_at": "2026-01-12T10:00:00Z"
    }
  ]
}
```

### Create Task

**Request:**
```http
POST /api/v1/tasks/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "project": 1,
  "title": "Write unit tests",
  "description": "Add unit tests for homepage components",
  "status": "todo",
  "priority": "medium",
  "due_date": "2026-01-25"
}
```

**Response:**
```json
{
  "id": 4,
  "project": 1,
  "project_name": "Website Redesign",
  "title": "Write unit tests",
  "description": "Add unit tests for homepage components",
  "status": "todo",
  "priority": "medium",
  "due_date": "2026-01-25",
  "created_at": "2026-01-12T11:00:00Z",
  "updated_at": "2026-01-12T11:00:00Z"
}
```

### Get Task Details (with Project Info)

**Request:**
```http
GET /api/v1/tasks/1/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "id": 1,
  "project": 1,
  "project_name": "Website Redesign",
  "title": "Design wireframes",
  "description": "Create wireframes for all pages",
  "status": "done",
  "priority": "high",
  "due_date": null,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T10:00:00Z",
  "project_details": {
    "id": 1,
    "name": "Website Redesign",
    "description": "Redesign company website with modern UI",
    "status": "active",
    "tasks_count": 3,
    "created_at": "2026-01-12T10:00:00Z",
    "updated_at": "2026-01-12T10:00:00Z"
  }
}
```

### Filter Tasks by Status

**Request:**
```http
GET /api/v1/tasks/by-status/?status=todo
Authorization: Bearer <your-token>
```

**Response:**
```json
[
  {
    "id": 4,
    "project": 1,
    "project_name": "Website Redesign",
    "title": "Write unit tests",
    "description": "Add unit tests for homepage components",
    "status": "todo",
    "priority": "medium",
    "due_date": "2026-01-25",
    "created_at": "2026-01-12T11:00:00Z",
    "updated_at": "2026-01-12T11:00:00Z"
  }
]
```

### Mark Task as Complete

**Request:**
```http
POST /api/v1/tasks/4/complete/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "id": 4,
  "project": 1,
  "project_name": "Website Redesign",
  "title": "Write unit tests",
  "description": "Add unit tests for homepage components",
  "status": "done",
  "priority": "medium",
  "due_date": "2026-01-25",
  "created_at": "2026-01-12T11:00:00Z",
  "updated_at": "2026-01-12T11:30:00Z"
}
```

---

## Documents

### List Documents (Tenant-Scoped)

**Request:**
```http
GET /api/v1/documents/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "project": 1,
      "project_name": "Website Redesign",
      "name": "Design Specifications.pdf",
      "file_path": "/uploads/acme/design-specs.pdf",
      "file_size": 2048576,
      "content_type": "application/pdf",
      "metadata": {
        "author": "Design Team",
        "version": "1.0"
      },
      "created_at": "2026-01-12T10:00:00Z",
      "updated_at": "2026-01-12T10:00:00Z"
    }
  ]
}
```

### Create Document

**Request:**
```http
POST /api/v1/documents/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "project": 1,
  "name": "Technical Requirements.docx",
  "file_path": "/uploads/acme/tech-requirements.docx",
  "file_size": 512000,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "metadata": {
    "author": "Product Manager",
    "version": "2.0"
  }
}
```

**Response:**
```json
{
  "id": 2,
  "project": 1,
  "project_name": "Website Redesign",
  "name": "Technical Requirements.docx",
  "file_path": "/uploads/acme/tech-requirements.docx",
  "file_size": 512000,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "metadata": {
    "author": "Product Manager",
    "version": "2.0"
  },
  "created_at": "2026-01-12T11:00:00Z",
  "updated_at": "2026-01-12T11:00:00Z"
}
```

### Filter Documents by Project

**Request:**
```http
GET /api/v1/documents/?project=1
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [...]
}
```

---

## Error Handling

### Invalid Token

**Request:**
```http
GET /api/v1/projects/
Authorization: Bearer invalid-token
```

**Response:**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```
Status: `401 Unauthorized`

### Missing Tenant Claim

**Response:**
```json
{
  "detail": "Token must include 'tenant' claim",
  "status_code": 401
}
```
Status: `401 Unauthorized`

### Inactive Tenant

**Response:**
```json
{
  "error": "Tenant 'acme' is not active",
  "status": 403
}
```
Status: `403 Forbidden`

### Cross-Tenant Access Attempt

**Request:**
```http
POST /api/v1/tasks/
Authorization: Bearer <tenant-a-token>
Content-Type: application/json

{
  "project": 999,  // Project belongs to Tenant B
  "title": "Task",
  "status": "todo"
}
```

**Response:**
```json
{
  "project": [
    "Project does not belong to your tenant"
  ],
  "status_code": 400,
  "tenant": "tenant-a"
}
```
Status: `400 Bad Request`

### Resource Not Found (Due to Tenant Filtering)

**Request:**
```http
GET /api/v1/projects/999/
Authorization: Bearer <tenant-a-token>
```

**Response:**
```json
{
  "detail": "Not found.",
  "status_code": 404
}
```
Status: `404 Not Found`

*Note: Even if project 999 exists for another tenant, it returns 404 due to tenant filtering.*

---

## Advanced Scenarios

### Pagination

**Request:**
```http
GET /api/v1/projects/?page=2
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "count": 120,
  "next": "http://localhost:8000/api/v1/projects/?page=3",
  "previous": "http://localhost:8000/api/v1/projects/?page=1",
  "results": [...]
}
```

### Filtering with Multiple Parameters

**Request:**
```http
GET /api/v1/tasks/?status=todo&priority=high
Authorization: Bearer <your-token>
```

### Service-to-Service Authentication

**Token Generation (Python):**
```python
from apps.authentication.utils import generate_service_token

token = generate_service_token(
    tenant=tenant_instance,
    service_name='payment-service',
    expiration_minutes=60
)
```

**Request:**
```http
GET /api/v1/projects/
Authorization: Bearer <service-token>
```

The request will have `request.service_name` set, indicating it's a service-to-service call.

---

## cURL Examples

### Complete Workflow

```bash
# 1. Get test tokens
TOKEN=$(cat test_tokens.json | jq -r '.tenants[0].access_token')

# 2. List projects
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/

# 3. Create a project
PROJECT_ID=$(curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"API Testing","description":"Testing the API","status":"active"}' \
  http://localhost:8000/api/v1/projects/ | jq -r '.id')

# 4. Create a task for that project
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project\":$PROJECT_ID,\"title\":\"Test task\",\"status\":\"todo\",\"priority\":\"high\"}" \
  http://localhost:8000/api/v1/tasks/

# 5. List tasks
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/tasks/

# 6. Get statistics
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/projects/statistics/
```

---

**Note:** All examples assume you've run `python manage.py create_test_data` to generate test data and tokens.
