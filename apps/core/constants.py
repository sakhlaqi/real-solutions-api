"""
Application-wide constants.
Centralizes all magic strings and constant values for better maintainability.
"""

from enum import Enum
from typing import Final


# =============================================================================
# JWT CLAIM NAMES
# =============================================================================
class JWTClaims:
    """Standard JWT claim names used throughout the application."""
    
    TENANT: Final[str] = 'tenant'
    TENANT_ID: Final[str] = 'tenant_id'  # Deprecated: use TENANT for consistency
    USER_ID: Final[str] = 'user_id'
    CLIENT_ID: Final[str] = 'client_id'
    CLIENT_TYPE: Final[str] = 'client_type'
    TOKEN_VERSION: Final[str] = 'token_version'
    SERVICE: Final[str] = 'service'
    ROLES: Final[str] = 'roles'
    SCOPES: Final[str] = 'scopes'
    ISSUER: Final[str] = 'iss'
    AUDIENCE: Final[str] = 'aud'
    SUBJECT: Final[str] = 'sub'
    EXPIRATION: Final[str] = 'exp'
    ISSUED_AT: Final[str] = 'iat'
    JWT_ID: Final[str] = 'jti'


# =============================================================================
# CLIENT TYPES
# =============================================================================
class ClientType(str, Enum):
    """API client types for different authentication scenarios."""
    
    SERVICE_ACCOUNT = 'service_account'
    USER = 'user'
    SERVICE = 'service'


# =============================================================================
# AUTHENTICATION TYPES
# =============================================================================
class AuthType(str, Enum):
    """Request authentication type identifiers."""
    
    USER = 'user'
    API_CLIENT = 'api_client'
    SERVICE = 'service'


# =============================================================================
# PROJECT STATUS
# =============================================================================
class ProjectStatus(str, Enum):
    """Project lifecycle status values."""
    
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'
    PENDING = 'pending'
    
    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.title()) for item in cls]


# =============================================================================
# TASK STATUS
# =============================================================================
class TaskStatus(str, Enum):
    """Task status values."""
    
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    IN_REVIEW = 'in_review'
    COMPLETED = 'completed'
    BLOCKED = 'blocked'
    
    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]


# =============================================================================
# TASK PRIORITY
# =============================================================================
class TaskPriority(str, Enum):
    """Task priority levels."""
    
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.title()) for item in cls]


# =============================================================================
# API SCOPES
# =============================================================================
class APIScopes:
    """Standard API scopes for permission control."""
    
    # Project scopes
    READ_PROJECTS: Final[str] = 'read:projects'
    WRITE_PROJECTS: Final[str] = 'write:projects'
    DELETE_PROJECTS: Final[str] = 'delete:projects'
    
    # Task scopes
    READ_TASKS: Final[str] = 'read:tasks'
    WRITE_TASKS: Final[str] = 'write:tasks'
    DELETE_TASKS: Final[str] = 'delete:tasks'
    
    # Document scopes
    READ_DOCUMENTS: Final[str] = 'read:documents'
    WRITE_DOCUMENTS: Final[str] = 'write:documents'
    DELETE_DOCUMENTS: Final[str] = 'delete:documents'
    
    # Admin scopes
    ADMIN: Final[str] = 'admin'
    TENANT_ADMIN: Final[str] = 'tenant:admin'


# =============================================================================
# API ROLES
# =============================================================================
class APIRoles:
    """Standard API roles for role-based access control."""
    
    ADMIN: Final[str] = 'admin'
    WRITE: Final[str] = 'write'
    READ: Final[str] = 'read'


# =============================================================================
# HTTP STATUS MESSAGES
# =============================================================================
class ErrorMessages:
    """Standardized error messages."""
    
    # Authentication errors
    INVALID_CREDENTIALS: Final[str] = 'Invalid credentials'
    TOKEN_EXPIRED: Final[str] = 'Token has expired'
    TOKEN_REVOKED: Final[str] = 'Token has been revoked'
    TOKEN_INVALID: Final[str] = 'Invalid token'
    AUTHENTICATION_REQUIRED: Final[str] = 'Authentication required'
    
    # Tenant errors
    TENANT_NOT_FOUND: Final[str] = 'Tenant not found'
    TENANT_INACTIVE: Final[str] = 'Tenant is not active'
    TENANT_REQUIRED: Final[str] = 'Tenant identification required'
    TENANT_MISMATCH: Final[str] = 'Tenant mismatch'
    
    # Permission errors
    PERMISSION_DENIED: Final[str] = 'You do not have permission to perform this action'
    CROSS_TENANT_ACCESS: Final[str] = 'Access to other tenant data is not allowed'
    
    # Validation errors
    VALIDATION_FAILED: Final[str] = 'Validation failed'
    INVALID_REQUEST: Final[str] = 'Invalid request'


# =============================================================================
# PAGINATION DEFAULTS
# =============================================================================
class PaginationDefaults:
    """Default pagination settings."""
    
    PAGE_SIZE: Final[int] = 50
    MAX_PAGE_SIZE: Final[int] = 200
    PAGE_QUERY_PARAM: Final[str] = 'page'
    PAGE_SIZE_QUERY_PARAM: Final[str] = 'page_size'
