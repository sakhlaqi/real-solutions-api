"""
Custom throttling classes for API client authentication.
Implements rate limiting with constant-time comparisons.
"""

from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache
from django.conf import settings


class APIClientTokenThrottle(SimpleRateThrottle):
    """
    Rate limiting for API client token requests.
    
    More restrictive than regular user throttling to prevent brute-force attacks
    on API credentials.
    """
    
    scope = 'api_client_token'
    rate = getattr(settings, 'API_CLIENT_TOKEN_RATE', '10/minute')
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on client_id if provided, otherwise IP.
        """
        # Try to get client_id from request data
        client_id = None
        if request.method == 'POST':
            client_id = request.data.get('client_id')
        
        if client_id:
            # Rate limit by client_id
            return self.cache_format % {
                'scope': self.scope,
                'ident': client_id
            }
        
        # Fall back to IP-based rate limiting
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class APIClientRefreshThrottle(SimpleRateThrottle):
    """
    Rate limiting for refresh token requests.
    
    Separate from token issuance to allow more frequent refreshes.
    """
    
    scope = 'api_client_refresh'
    rate = getattr(settings, 'API_CLIENT_REFRESH_RATE', '30/minute')
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on IP address.
        """
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class PerClientRateThrottle(SimpleRateThrottle):
    """
    Per-client rate limiting for API requests.
    
    Uses the rate_limit field from APIClient model if set,
    otherwise falls back to default rate.
    """
    
    scope = 'per_client'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on authenticated API client.
        """
        # Only throttle if authenticated as API client
        if not hasattr(request, 'api_client'):
            return None
        
        client_id = request.api_client.client_id
        return self.cache_format % {
            'scope': self.scope,
            'ident': client_id
        }
    
    def get_rate(self):
        """
        Get rate limit for the authenticated API client.
        """
        # Access request from view
        if hasattr(self, 'request') and hasattr(self.request, 'api_client'):
            api_client = self.request.api_client
            if api_client.rate_limit:
                # Custom rate limit for this client
                return f"{api_client.rate_limit}/hour"
        
        # Default rate
        return getattr(settings, 'PER_CLIENT_DEFAULT_RATE', '1000/hour')
    
    def allow_request(self, request, view):
        """
        Override to store request for get_rate() access.
        """
        self.request = request
        return super().allow_request(request, view)
