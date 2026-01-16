"""
Registry of public endpoints that don't require authentication.

This centralized configuration is used by TenantMiddleware to determine
which endpoints should skip authentication checks.

URL patterns are registered by their app:name notation for maintainability.
"""

from typing import Set, List, Dict
from dataclasses import dataclass


@dataclass
class PublicEndpoint:
    """Configuration for a public endpoint."""
    url_name: str  # Django URL name (e.g., 'authentication:login')
    methods: Set[str] = None  # HTTP methods allowed, None = all methods
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'}


# Public authentication endpoints
PUBLIC_AUTH_ENDPOINTS = [
    PublicEndpoint('authentication:login', {'POST'}),
    PublicEndpoint('authentication:register', {'POST'}),
    PublicEndpoint('authentication:token_obtain', {'POST'}),
    PublicEndpoint('authentication:token_refresh', {'POST'}),
    PublicEndpoint('authentication:token_verify', {'POST'}),
    PublicEndpoint('authentication:api_client_token', {'POST'}),
    PublicEndpoint('authentication:api_client_refresh', {'POST'}),
]

# Public tenant endpoints
PUBLIC_TENANT_ENDPOINTS = [
    PublicEndpoint('tenants:tenant-by-slug', {'GET'}),
    PublicEndpoint('tenants:tenant-config-by-slug', {'GET'}),
]

# Public documentation endpoints
PUBLIC_DOC_ENDPOINTS = [
    'schema',
    'swagger-ui',
    'redoc',
]

# Combine all public endpoints
PUBLIC_ENDPOINTS = PUBLIC_AUTH_ENDPOINTS + PUBLIC_TENANT_ENDPOINTS


def get_public_url_names() -> Set[str]:
    """Get set of all public URL names for quick lookup."""
    url_names = {ep.url_name for ep in PUBLIC_ENDPOINTS}
    url_names.update(PUBLIC_DOC_ENDPOINTS)
    return url_names


def is_method_allowed(url_name: str, method: str) -> bool:
    """Check if HTTP method is allowed for a public endpoint."""
    for endpoint in PUBLIC_ENDPOINTS:
        if endpoint.url_name == url_name:
            return method.upper() in endpoint.methods
    return True  # Doc endpoints allow all methods
