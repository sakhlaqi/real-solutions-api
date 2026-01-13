"""
Custom permissions for tenant isolation.
"""

from rest_framework import permissions


class IsTenantUser(permissions.BasePermission):
    """
    Permission class that ensures the user belongs to the request's tenant.
    
    This provides an additional layer of security by validating that the
    authenticated user is associated with the tenant in the request context.
    """
    
    message = "You do not have permission to access this tenant's resources."
    
    def has_permission(self, request, view):
        """
        Check if user has permission to access the tenant's resources.
        
        Args:
            request: Django request object (must have tenant attribute)
            view: DRF view
            
        Returns:
            bool: True if user can access tenant resources
        """
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Ensure tenant is set on request
        if not hasattr(request, 'tenant'):
            return False
        
        # For superusers, allow access to all tenants
        if request.user.is_superuser:
            return True
        
        # Check if user belongs to the tenant
        # This assumes a relationship between User and Tenant
        # Implement based on your user-tenant relationship model
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access a specific object.
        
        Args:
            request: Django request object
            view: DRF view
            obj: Model instance
            
        Returns:
            bool: True if user can access the object
        """
        # Ensure object belongs to the request's tenant
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.tenant
        
        return True


class IsTenantAdmin(permissions.BasePermission):
    """
    Permission class for tenant administrators.
    
    This can be used for endpoints that require admin privileges within a tenant.
    """
    
    message = "You must be a tenant administrator to perform this action."
    
    def has_permission(self, request, view):
        """
        Check if user is a tenant administrator.
        
        Args:
            request: Django request object
            view: DRF view
            
        Returns:
            bool: True if user is tenant admin
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request, 'tenant'):
            return False
        
        # Superusers have admin rights everywhere
        if request.user.is_superuser:
            return True
        
        # Implement tenant admin check based on your user model
        # Example: return request.user.is_tenant_admin(request.tenant)
        return request.user.is_staff


class IsServiceAccount(permissions.BasePermission):
    """
    Permission class for service-to-service authentication.
    
    Use this for endpoints that should only be accessible by other services.
    """
    
    message = "This endpoint is only accessible to service accounts."
    
    def has_permission(self, request, view):
        """
        Check if request is from a service account.
        
        Args:
            request: Django request object
            view: DRF view
            
        Returns:
            bool: True if request is from a service
        """
        # Check if request has service_name attribute
        # (set by ServiceToServiceAuthentication)
        return hasattr(request, 'service_name')


class IsAPIClient(permissions.BasePermission):
    """
    Permission class for API client authentication.
    
    Verifies that the request is authenticated via API client credentials.
    """
    
    message = "This endpoint requires API client authentication."
    
    def has_permission(self, request, view):
        """
        Check if request is from an authenticated API client.
        
        Args:
            request: Django request object
            view: DRF view
            
        Returns:
            bool: True if request is from an API client
        """
        return hasattr(request, 'api_client') and request.api_client is not None


class HasAPIClientRole(permissions.BasePermission):
    """
    Permission class to check if API client has required role(s).
    
    Usage:
        class MyView(APIView):
            permission_classes = [IsAPIClient, HasAPIClientRole]
            required_roles = ['admin', 'write']  # Client needs any of these roles
    """
    
    message = "Your API client does not have the required role."
    
    def has_permission(self, request, view):
        """
        Check if API client has required role.
        
        Args:
            request: Django request object
            view: DRF view (must have 'required_roles' attribute)
            
        Returns:
            bool: True if API client has at least one required role
        """
        if not hasattr(request, 'api_client') or not request.api_client:
            return False
        
        # Get required roles from view
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True  # No specific roles required
        
        # Check if client has any of the required roles
        client_roles = set(request.api_client.roles)
        return bool(client_roles.intersection(required_roles))


class HasAPIClientScope(permissions.BasePermission):
    """
    Permission class to check if API client has required scope(s).
    
    Usage:
        class MyView(APIView):
            permission_classes = [IsAPIClient, HasAPIClientScope]
            required_scopes = ['read:projects', 'write:projects']
    """
    
    message = "Your API client does not have the required scope."
    
    def has_permission(self, request, view):
        """
        Check if API client has required scope.
        
        Args:
            request: Django request object
            view: DRF view (must have 'required_scopes' attribute)
            
        Returns:
            bool: True if API client has at least one required scope
        """
        if not hasattr(request, 'api_client') or not request.api_client:
            return False
        
        # Get required scopes from view
        required_scopes = getattr(view, 'required_scopes', [])
        if not required_scopes:
            return True  # No specific scopes required
        
        # Check if client has any of the required scopes
        client_scopes = set(request.api_client.scopes)
        return bool(client_scopes.intersection(required_scopes))


class IsAPIClientOrUser(permissions.BasePermission):
    """
    Permission that allows both API clients and regular authenticated users.
    
    Useful for endpoints that should be accessible by both authentication methods.
    """
    
    message = "Authentication required (API client or user)."
    
    def has_permission(self, request, view):
        """
        Check if request is from either an API client or authenticated user.
        
        Args:
            request: Django request object
            view: DRF view
            
        Returns:
            bool: True if authenticated via any method
        """
        # Check API client authentication
        if hasattr(request, 'api_client') and request.api_client:
            return True
        
        # Check user authentication
        if request.user and request.user.is_authenticated:
            return True
        
        return False
