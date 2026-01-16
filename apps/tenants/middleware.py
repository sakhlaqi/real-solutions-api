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
import re
import time
import uuid
from typing import Optional, List, Set
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
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
    """
    
    # Cached set of public paths for O(1) lookup
    _public_paths: Set[str] = {
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',
        '/api/v1/auth/token/',
        '/api/v1/auth/token/refresh/',
        '/api/v1/auth/token/verify/',
        '/api/v1/auth/api-client/token/',
        '/api/v1/auth/api-client/token/refresh/',
        '/api/v1/auth/login/',
        '/api/v1/auth/register/',
        '/api/v1/auth/logout/',
    }
    
    # Compiled regex patterns for dynamic public routes
    _public_patterns: List[re.Pattern] = [
        re.compile(r'^/api/v1/tenants/[a-z0-9-]+/?$'),  # GET /tenants/{slug}/
        re.compile(r'^/api/v1/tenants/[a-z0-9-]+/config/?$'),  # GET /tenants/{slug}/config/
        re.compile(r'^/api/v1/auth/me/?$'),  # GET /auth/me/ needs auth but handled separately
    ]
    
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
        # Skip non-API and public paths
        if not request.path.startswith('/api/') or self._is_public_path(request.path):
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
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is a public endpoint.
        
        Uses both exact match and regex patterns for flexibility.
        """
        # Exact match first (O(1))
        if path.rstrip('/') + '/' in self._public_paths or path in self._public_paths:
            return True
        
        # Regex patterns for dynamic routes
        return any(pattern.match(path) for pattern in self._public_patterns)
    
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
