"""
Custom JWT Authentication with tenant extraction.
"""

import logging
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from apps.tenants.models import Tenant

logger = logging.getLogger(__name__)


class TenantJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that validates tenant claim and attaches tenant to request.
    
    This authentication class extends djangorestframework-simplejwt's JWTAuthentication
    to add tenant-specific validation:
    
    1. Validates JWT signature and expiration (via parent class)
    2. Extracts and validates the 'tenant' claim from the token
    3. Resolves the Tenant object from the database
    4. Validates tenant is active
    5. Attaches tenant to the request object
    
    The tenant claim must be present in the JWT token and must reference an active tenant.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and extract tenant information.
        
        Args:
            request: Django request object
            
        Returns:
            tuple: (user, validated_token) or None
            
        Raises:
            AuthenticationFailed: If authentication fails
            InvalidToken: If token is invalid
        """
        # Call parent authentication to validate JWT
        result = super().authenticate(request)
        
        if result is None:
            return None
        
        user, validated_token = result
        
        # Extract and validate tenant from token
        try:
            tenant = self._get_tenant_from_token(validated_token)
            
            # Attach tenant to request for use in views
            request.tenant = tenant
            
            logger.debug(
                f"Authenticated user {user.id} for tenant {tenant.slug}"
            )
            
        except Tenant.DoesNotExist:
            logger.warning(
                f"Tenant not found in token for user {user.id}"
            )
            raise AuthenticationFailed(
                'Tenant specified in token does not exist'
            )
        except Exception as e:
            logger.error(
                f"Tenant validation error: {str(e)}", 
                exc_info=True
            )
            raise AuthenticationFailed(
                'Tenant validation failed'
            )
        
        return user, validated_token
    
    def _get_tenant_from_token(self, token):
        """
        Extract and validate tenant from JWT token.
        
        Args:
            token: Validated JWT token object
            
        Returns:
            Tenant instance
            
        Raises:
            AuthenticationFailed: If tenant claim is missing or invalid
            Tenant.DoesNotExist: If tenant doesn't exist in database
        """
        # Get tenant claim name from settings
        tenant_claim = getattr(settings, 'TENANT_CLAIM_NAME', 'tenant')
        
        # Extract tenant ID from token
        tenant_id = token.get(tenant_claim)
        
        if not tenant_id:
            logger.warning(
                f"JWT token missing required '{tenant_claim}' claim"
            )
            raise AuthenticationFailed(
                f"Token must include '{tenant_claim}' claim"
            )
        
        # Fetch tenant from database
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            logger.warning(f"Invalid tenant ID in token: {tenant_id}")
            raise
        
        # Validate tenant is active
        if not tenant.is_active:
            logger.warning(
                f"Attempt to authenticate with inactive tenant: {tenant.slug}"
            )
            raise AuthenticationFailed(
                f"Tenant '{tenant.slug}' is not active"
            )
        
        return tenant


class ServiceToServiceAuthentication(JWTAuthentication):
    """
    Authentication class for service-to-service communication.
    
    This can be used for inter-service API calls where a service account
    or system token is used instead of a user token.
    
    The token should include:
    - 'tenant' claim (required)
    - 'service' claim identifying the calling service
    - 'iss' and 'aud' claims for additional validation
    """
    
    def authenticate(self, request):
        """
        Authenticate service-to-service requests.
        
        Args:
            request: Django request object
            
        Returns:
            tuple: (None, validated_token) - no user for service tokens
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        result = super().authenticate(request)
        
        if result is None:
            return None
        
        user, validated_token = result
        
        # Extract tenant and service claims
        try:
            tenant = self._get_tenant_from_token(validated_token)
            service_name = validated_token.get('service')
            
            if not service_name:
                raise AuthenticationFailed(
                    "Service-to-service token must include 'service' claim"
                )
            
            # Attach context to request
            request.tenant = tenant
            request.service_name = service_name
            
            logger.info(
                f"Service-to-service auth: {service_name} -> tenant {tenant.slug}"
            )
            
        except Exception as e:
            logger.error(f"Service auth error: {str(e)}", exc_info=True)
            raise AuthenticationFailed('Service authentication failed')
        
        # Return None for user since this is a service token
        return None, validated_token
    
    def _get_tenant_from_token(self, token):
        """Extract tenant from token (same as TenantJWTAuthentication)."""
        tenant_claim = getattr(settings, 'TENANT_CLAIM_NAME', 'tenant')
        tenant_id = token.get(tenant_claim)
        
        if not tenant_id:
            raise AuthenticationFailed(
                f"Token must include '{tenant_claim}' claim"
            )
        
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            raise AuthenticationFailed('Invalid tenant in token')
        
        if not tenant.is_active:
            raise AuthenticationFailed(f"Tenant '{tenant.slug}' is not active")
        
        return tenant
