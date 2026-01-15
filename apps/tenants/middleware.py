"""
Middleware for tenant resolution and request lifecycle management.
"""

import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Tenant

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that resolves tenant context from JWT token and attaches it to the request.
    
    This middleware:
    1. Extracts the JWT token from the Authorization header
    2. Validates the token and extracts the tenant claim
    3. Resolves the Tenant object from the database
    4. Attaches the tenant to request.tenant
    5. Validates tenant is active
    
    This runs AFTER authentication middleware, so the token has already been validated
    by the authentication backend. This middleware focuses on tenant resolution.
    """
    
    def process_request(self, request):
        """
        Process incoming request to extract and validate tenant context.
        """
        # Skip tenant resolution for non-API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Check if this is a public tenant endpoint (by slug)
        import re
        if re.match(r'^/api/v1/tenants/[^/]+/?$', request.path):
            # GET /tenants/{slug}/
            return None
        if re.match(r'^/api/v1/tenants/[^/]+/config/?$', request.path):
            # GET /tenants/{slug}/config/
            return None
        
        # Skip for public endpoints (schema, docs, auth)
        public_paths = [
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
        ]
        if any(request.path.startswith(path) for path in public_paths):
            return None
        
        # Extract tenant from JWT token
        try:
            tenant = self._extract_tenant_from_request(request)
            
            if tenant is None:
                return self._error_response(
                    "Tenant identification required",
                    status=401
                )
            
            # Validate tenant is active
            if not tenant.is_active:
                return self._error_response(
                    f"Tenant '{tenant.slug}' is not active",
                    status=403
                )
            
            # Attach tenant to request
            request.tenant = tenant
            
            logger.debug(
                f"Tenant resolved: {tenant.slug} for path {request.path}"
            )
            
        except Tenant.DoesNotExist:
            return self._error_response(
                "Invalid tenant identifier",
                status=403
            )
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Token validation error: {str(e)}")
            return self._error_response(
                "Invalid or expired authentication token",
                status=401
            )
        except Exception as e:
            logger.error(f"Tenant resolution error: {str(e)}", exc_info=True)
            return self._error_response(
                "Tenant resolution failed",
                status=500
            )
        
        return None
    
    def _extract_tenant_from_request(self, request):
        """
        Extract tenant from JWT token in request.
        
        Args:
            request: Django request object
            
        Returns:
            Tenant instance or None
        """
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extract token
        token_string = auth_header.split('Bearer ')[1]
        
        try:
            # Decode token
            token = AccessToken(token_string)
            
            # Extract tenant claim
            tenant_claim = getattr(settings, 'TENANT_CLAIM_NAME', 'tenant')
            tenant_id = token.get(tenant_claim)
            
            if not tenant_id:
                logger.warning(
                    f"JWT token missing '{tenant_claim}' claim"
                )
                return None
            
            # Resolve tenant from database
            tenant = Tenant.objects.get(id=tenant_id)
            return tenant
            
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Token decode error: {str(e)}")
            raise
        except Tenant.DoesNotExist:
            logger.warning(f"Tenant not found: {tenant_id}")
            raise
    
    def _error_response(self, message, status=400):
        """
        Return a JSON error response.
        
        Args:
            message: Error message
            status: HTTP status code
            
        Returns:
            JsonResponse
        """
        return JsonResponse(
            {
                'error': message,
                'status': status
            },
            status=status
        )
