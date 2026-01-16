"""
Custom exception handlers and error responses.

Provides consistent error response format across the API:
{
    "error": {
        "code": "error_code",
        "message": "Human-readable message",
        "details": {...}  // Optional additional context
    },
    "status_code": 400,
    "tenant": "tenant-slug"  // If available
}
"""

from typing import Optional, Dict, Any
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    Custom exception handler that provides consistent error responses.
    
    This enhances the default DRF exception handler with:
    - Structured error responses
    - Tenant context logging
    - Correlation ID tracking
    - Consistent error format
    """
    # Get request context
    request = context.get('request')
    correlation_id = getattr(request, 'correlation_id', None) if request else None
    
    # Get tenant context for logging
    tenant_slug = None
    if request and hasattr(request, 'tenant') and request.tenant:
        tenant_slug = request.tenant.slug
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception with context
    log_extra = {
        'tenant': tenant_slug or 'unknown',
        'path': request.path if request else 'unknown',
        'method': request.method if request else 'unknown',
        'correlation_id': correlation_id,
    }
    
    if response is None:
        # Unhandled exception - log as error
        logger.error(
            f"Unhandled exception for tenant {tenant_slug}: {str(exc)}",
            exc_info=True,
            extra=log_extra
        )
        # Return generic server error
        return Response(
            {
                'error': {
                    'code': 'internal_error',
                    'message': 'An unexpected error occurred',
                },
                'status_code': 500,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Log handled exceptions at appropriate level
    if response.status_code >= 500:
        logger.error(
            f"API error for tenant {tenant_slug}: {str(exc)}",
            exc_info=True,
            extra=log_extra
        )
    elif response.status_code >= 400:
        logger.warning(
            f"API warning for tenant {tenant_slug}: {str(exc)}",
            extra=log_extra
        )
    
    # Standardize error response format
    error_data = _format_error_response(exc, response, tenant_slug, correlation_id)
    response.data = error_data
    
    return response


def _format_error_response(
    exc: Exception,
    response: Response,
    tenant_slug: Optional[str],
    correlation_id: Optional[str]
) -> Dict[str, Any]:
    """
    Format exception into standardized error response.
    """
    # Determine error code
    error_code = getattr(exc, 'default_code', None) or _get_error_code(exc, response)
    
    # Get error message
    if isinstance(exc, ValidationError):
        message = 'Validation failed'
        details = response.data if isinstance(response.data, dict) else {'errors': response.data}
    elif hasattr(exc, 'detail'):
        message = str(exc.detail) if not isinstance(exc.detail, dict) else 'Request failed'
        details = exc.detail if isinstance(exc.detail, dict) else None
    else:
        message = str(exc)
        details = None
    
    # Build response
    error_response = {
        'error': {
            'code': error_code,
            'message': message,
        },
        'status_code': response.status_code,
    }
    
    if details:
        error_response['error']['details'] = details
    
    if tenant_slug:
        error_response['tenant'] = tenant_slug
    
    if correlation_id:
        error_response['correlation_id'] = correlation_id
    
    return error_response


def _get_error_code(exc: Exception, response: Response) -> str:
    """
    Derive error code from exception type and status code.
    """
    status_code = response.status_code
    
    if status_code == 400:
        return 'bad_request'
    elif status_code == 401:
        return 'unauthorized'
    elif status_code == 403:
        return 'forbidden'
    elif status_code == 404:
        return 'not_found'
    elif status_code == 405:
        return 'method_not_allowed'
    elif status_code == 429:
        return 'rate_limited'
    elif status_code >= 500:
        return 'server_error'
    else:
        return 'unknown_error'


# =============================================================================
# CUSTOM EXCEPTION CLASSES
# =============================================================================

class TenantNotFoundError(APIException):
    """Exception raised when tenant cannot be resolved."""
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Tenant not found or inactive'
    default_code = 'tenant_not_found'


class TenantValidationError(APIException):
    """Exception raised when tenant validation fails."""
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Tenant validation failed'
    default_code = 'tenant_validation_error'


class CrossTenantAccessError(APIException):
    """Exception raised when attempting to access data from another tenant."""
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Access to other tenant data is not allowed'
    default_code = 'cross_tenant_access'


class TenantInactiveError(APIException):
    """Exception raised when tenant is inactive."""
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Tenant is not active'
    default_code = 'tenant_inactive'


class ResourceNotFoundError(APIException):
    """Exception raised when a specific resource is not found."""
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'resource_not_found'
    
    def __init__(self, resource_type: str = 'Resource', detail: str = None):
        if detail is None:
            detail = f'{resource_type} not found'
        super().__init__(detail=detail)


class TokenRevokedError(APIException):
    """Exception raised when a revoked token is used."""
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token has been revoked'
    default_code = 'token_revoked'
