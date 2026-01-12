"""
Utilities for JWT token generation with tenant claims.
"""

import uuid
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import jwt


def generate_tenant_token(user, tenant, extra_claims=None):
    """
    Generate a JWT token with tenant claim for a user.
    
    This is a utility function for generating tokens programmatically,
    useful for testing, service accounts, or custom authentication flows.
    
    Args:
        user: Django User instance
        tenant: Tenant instance or tenant ID (UUID)
        extra_claims: Optional dict of additional claims to include
        
    Returns:
        dict: Contains 'access' and 'refresh' tokens
    """
    # Get tenant ID
    tenant_id = str(tenant.id if hasattr(tenant, 'id') else tenant)
    
    # Create refresh token
    refresh = RefreshToken.for_user(user)
    
    # Add tenant claim
    tenant_claim = getattr(settings, 'TENANT_CLAIM_NAME', 'tenant')
    refresh[tenant_claim] = tenant_id
    
    # Add any extra claims
    if extra_claims:
        for key, value in extra_claims.items():
            refresh[key] = value
    
    # Return both access and refresh tokens
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def generate_service_token(tenant, service_name, expiration_minutes=60):
    """
    Generate a service-to-service JWT token.
    
    This creates a token for inter-service communication that includes
    the tenant claim but no user information.
    
    Args:
        tenant: Tenant instance or tenant ID (UUID)
        service_name: Name of the calling service
        expiration_minutes: Token expiration time in minutes
        
    Returns:
        str: JWT token string
    """
    tenant_id = str(tenant.id if hasattr(tenant, 'id') else tenant)
    tenant_claim = getattr(settings, 'TENANT_CLAIM_NAME', 'tenant')
    
    # Create token payload
    now = datetime.utcnow()
    payload = {
        tenant_claim: tenant_id,
        'service': service_name,
        'iat': now,
        'exp': now + timedelta(minutes=expiration_minutes),
        'iss': settings.SIMPLE_JWT['ISSUER'],
        'aud': settings.SIMPLE_JWT['AUDIENCE'],
        'jti': str(uuid.uuid4()),
        'token_type': 'service',
    }
    
    # Encode token
    token = jwt.encode(
        payload,
        settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithm=settings.SIMPLE_JWT['ALGORITHM']
    )
    
    return token


def decode_token(token_string):
    """
    Decode and validate a JWT token.
    
    Args:
        token_string: JWT token string
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(
        token_string,
        settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
        audience=settings.SIMPLE_JWT['AUDIENCE'],
        issuer=settings.SIMPLE_JWT['ISSUER'],
    )


def extract_tenant_from_token(token_string):
    """
    Extract tenant ID from a JWT token.
    
    Args:
        token_string: JWT token string
        
    Returns:
        str: Tenant ID (UUID string)
        
    Raises:
        jwt.InvalidTokenError: If token is invalid
        KeyError: If tenant claim is missing
    """
    payload = decode_token(token_string)
    tenant_claim = getattr(settings, 'TENANT_CLAIM_NAME', 'tenant')
    return payload[tenant_claim]
