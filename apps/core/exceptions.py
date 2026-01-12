"""
Custom exception handlers and error responses.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    This enhances the default DRF exception handler with:
    - Tenant context logging
    - Structured error responses
    - Additional error details for debugging
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception with tenant context
    request = context.get('request')
    tenant_slug = getattr(request, 'tenant', None)
    tenant_slug = tenant_slug.slug if tenant_slug else 'unknown'
    
    logger.error(
        f"API Exception for tenant {tenant_slug}: {str(exc)}",
        exc_info=True,
        extra={
            'tenant': tenant_slug,
            'path': request.path if request else 'unknown',
            'method': request.method if request else 'unknown',
        }
    )
    
    # Enhance response with additional context
    if response is not None:
        response.data['status_code'] = response.status_code
        
        # Add tenant context to response (for debugging)
        if hasattr(request, 'tenant'):
            response.data['tenant'] = request.tenant.slug
    
    return response


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
