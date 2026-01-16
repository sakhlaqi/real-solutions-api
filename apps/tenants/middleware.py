"""
Middleware for tenant resolution and request lifecycle management.

This middleware works in conjunction with TenantJWTAuthentication to ensure
tenant context is properly established for all API requests.

Architecture Note:
------------------
Tenant extraction is handled by TenantJWTAuthentication for authenticated routes.
This middleware provides:
1. Early tenant validation for public routes that need tenant context
2. Logging and audit trail for tenant-scoped requests
3. Request lifecycle management (timing, correlation IDs)

The authentication class is the primary source of tenant context for protected routes.
"""

import logging
import time
import uuid
from typing import Optional
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.urls import resolve, Resolver404
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from apps.core.public_endpoints import get_public_url_names, is_method_allowed
from .models import Tenant

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware for tenant-aware request processing.
    
    This middleware:
    1. Skips processing for non-API and public endpoints
    2. Adds request correlation ID for tracing
    3. Logs tenant context for audit purposes
    4. Validates tenant is active (defense in depth)
    
    Note: Primary tenant extraction happens in TenantJWTAuthentication.
    This middleware adds logging and validation as a secondary check.
    
    Public endpoints are defined in apps.core.public_endpoints for centralized management.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        # Cache public URL names for performance
        self._public_url_names = get_public_url_names()
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request for tenant context.
        
        This method runs BEFORE authentication and view processing.
        """
        # Add correlation ID for request tracing
        request.correlation_id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Skip non-API endpoints entirely
        if not request.path.startswith('/api/'):
            return None
        
        # Skip public endpoints - tenant context handled elsewhere
        if self._is_public_path(request.path):
            return None
        
        # For authenticated endpoints, tenant extraction happens in
        # TenantJWTAuthentication. This middleware only logs and validates.
        return None
    
    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs) -> Optional[HttpResponse]:
        """
        Process view for tenant validation (defense in depth).
        
        This runs AFTER authentication but BEFORE the view.
        At this point, request.tenant should be set by TenantJWTAuthentication.
        """
        # Skip non-API and public endpoints
        if not request.path.startswith('/api/') or self._is_public_endpoint(request:
            return None
        
        # Check if tenant was set by authentication
        if hasattr(request, 'tenant') and request.tenant:
            # Defense in depth: validate tenant is still active
            if not request.tenant.is_active:
                logger.warning(
                    f"Request to deactivated tenant: {request.tenant.slug}",
                    extra={'correlation_id': getattr(request, 'correlation_id', 'N/A')}
                )
                return self._error_response(
                    f"Tenant '{request.tenant.slug}' is not active",
                    status=403
                )
            
            # Log successful tenant resolution for audit
            logger.debug(
                f"Tenant resolved: {request.tenant.slug} for {request.method} {request.path}",
                extra={
                    'tenant_slug': request.tenant.slug,
                    'tenant_id': str(request.tenant.id),
                    'correlation_id': getattr(request, 'correlation_id', 'N/A'),
                    'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                }
            )
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Add correlation ID and timing to response headers.
        """
        # Add correlation ID to response for client-side tracing
        if hasattr(request, 'correlation_id'):
            response['X-Correlation-ID'] = request.correlation_id
        
        # Add timing information (useful for debugging)
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
            response['X-Response-Time'] = f"{duration_ms:.2f}ms"
        
        return response
    
    def _is_public_endpoint(self, request: HttpRequest) -> bool:
        """
        Check if request path is a public endpoint using Django URL resolution.
        
        This method resolves the URL to its named pattern and checks against
        the centralized public endpoints registry.
        """
        try:
            # Resolve URL to its named pattern
            resolved = resolve(request.path)
            
            # Get full URL name (namespace:name or just name)
            if resolved.namespace:
                url_name = f"{resolved.namespace}:{resolved.url_name}"
            else:
                url_name = resolved.url_name
            
            # Check if URL is in public registry
            if url_name in self._public_url_names:
                # Verify HTTP method is allowed for this endpoint
                return is_method_allowed(url_name, request.method)
            
            return False
            
        except Resolver404:
            # URL doesn't exist, let Django handle the 404
            return False
        except Exception as e:
            # Log unexpected errors but don't block request
            logger.error(f"Error checking public endpoint: {e}", exc_info=True)
            return False
    
    def _error_response(self, message: str, status: int = 400) -> JsonResponse:
        """
        Return a standardized JSON error response.
        """
        return JsonResponse(
            {
                'error': message,
                'status': status,
                'code': 'tenant_error' if status == 403 else 'bad_request'
            },
            status=status
        )
