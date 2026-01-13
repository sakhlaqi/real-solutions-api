"""
Custom JWT token classes with enhanced claims for API clients.
Implements JWT best practices: iss, aud, sub, exp, iat, jti, and custom claims.
"""

import uuid
from datetime import datetime
from rest_framework_simplejwt.tokens import Token
from django.conf import settings


class APIClientAccessToken(Token):
    """
    Custom access token for API clients with enhanced claims.
    
    Includes:
    - Standard claims: iss (issuer), aud (audience), sub (subject), exp, iat, jti
    - Custom claims: tenant_id, tenant_slug, client_id, roles, scopes, token_version
    """
    
    token_type = 'access'
    lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add standard JWT claims if not present
        if 'iss' not in self.payload:
            self.payload['iss'] = settings.SIMPLE_JWT.get('ISSUER', 'multitenant-api')
        
        if 'aud' not in self.payload:
            self.payload['aud'] = settings.SIMPLE_JWT.get('AUDIENCE', 'multitenant-api')
    
    @classmethod
    def for_api_client(cls, api_client):
        """
        Create an access token for an API client.
        
        Args:
            api_client: APIClient instance
            
        Returns:
            APIClientAccessToken instance
        """
        token = cls()
        
        # Standard JWT claims
        token['iss'] = settings.SIMPLE_JWT.get('ISSUER', 'multitenant-api')
        token['aud'] = settings.SIMPLE_JWT.get('AUDIENCE', 'multitenant-api')
        token['sub'] = str(api_client.id)  # Subject: unique identifier for the client
        token['jti'] = str(uuid.uuid4())  # JWT ID: unique identifier for this token
        token['iat'] = int(datetime.utcnow().timestamp())  # Issued at
        
        # Custom claims for API client
        token['client_id'] = api_client.client_id
        token['client_type'] = 'service_account'
        
        # Tenant information
        token['tenant_id'] = str(api_client.tenant.id)
        token['tenant_slug'] = api_client.tenant.slug
        
        # Roles and scopes
        token['roles'] = api_client.roles
        token['scopes'] = api_client.scopes
        
        # Token versioning for revocation
        token['token_version'] = api_client.token_version
        
        # Token type
        token['token_type'] = cls.token_type
        
        return token


class APIClientRefreshToken(Token):
    """
    Custom refresh token for API clients.
    
    Longer-lived token used to obtain new access tokens.
    """
    
    token_type = 'refresh'
    lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add standard JWT claims if not present
        if 'iss' not in self.payload:
            self.payload['iss'] = settings.SIMPLE_JWT.get('ISSUER', 'multitenant-api')
        
        if 'aud' not in self.payload:
            self.payload['aud'] = settings.SIMPLE_JWT.get('AUDIENCE', 'multitenant-api')
    
    @classmethod
    def for_api_client(cls, api_client):
        """
        Create a refresh token for an API client.
        
        Args:
            api_client: APIClient instance
            
        Returns:
            APIClientRefreshToken instance
        """
        token = cls()
        
        # Standard JWT claims
        token['iss'] = settings.SIMPLE_JWT.get('ISSUER', 'multitenant-api')
        token['aud'] = settings.SIMPLE_JWT.get('AUDIENCE', 'multitenant-api')
        token['sub'] = str(api_client.id)
        token['jti'] = str(uuid.uuid4())
        token['iat'] = int(datetime.utcnow().timestamp())
        
        # Minimal claims for refresh token
        token['client_id'] = api_client.client_id
        token['client_type'] = 'service_account'
        token['tenant_id'] = str(api_client.tenant.id)
        token['token_version'] = api_client.token_version
        token['token_type'] = cls.token_type
        
        return token


def create_token_pair_for_api_client(api_client):
    """
    Create both access and refresh tokens for an API client.
    
    Args:
        api_client: APIClient instance
        
    Returns:
        dict: {
            'access': <access_token_string>,
            'refresh': <refresh_token_string>,
            'access_token_expires_at': <timestamp>,
            'refresh_token_expires_at': <timestamp>
        }
    """
    access_token = APIClientAccessToken.for_api_client(api_client)
    refresh_token = APIClientRefreshToken.for_api_client(api_client)
    
    return {
        'access': str(access_token),
        'refresh': str(refresh_token),
        'access_token_expires_at': access_token['exp'],
        'refresh_token_expires_at': refresh_token['exp'],
        'token_type': 'Bearer'
    }
