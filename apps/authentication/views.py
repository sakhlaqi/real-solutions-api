"""
Custom views for JWT token generation with tenant support.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that adds tenant claim to JWT token.
    
    Expects:
    - username: User's username
    - password: User's password
    - tenant: Tenant slug or ID (optional, will use user's default tenant if not provided)
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add tenant field (optional)
        self.fields['tenant'] = self.fields['username'].__class__(
            required=False,
            allow_blank=True,
            help_text="Tenant slug or ID"
        )
    
    @classmethod
    def get_token(cls, user):
        """
        Generate token with tenant claim.
        
        This method is called after authentication succeeds.
        We add the tenant claim to the token payload.
        """
        token = super().get_token(user)
        
        # Get tenant from request context (set in validate method)
        tenant = getattr(user, '_tenant_for_token', None)
        
        if tenant:
            # Add tenant claim
            token['tenant'] = str(tenant.id)
            token['tenant_slug'] = tenant.slug
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email if hasattr(user, 'email') else ''
        
        return token
    
    def validate(self, attrs):
        """
        Validate credentials and resolve tenant.
        """
        from apps.tenants.models import Tenant
        
        # Get tenant from request data
        tenant_identifier = attrs.pop('tenant', None)
        
        # Authenticate user
        data = super().validate(attrs)
        
        # Resolve tenant
        tenant = None
        if tenant_identifier:
            # Try to find tenant by slug or ID
            try:
                tenant = Tenant.objects.get(slug=tenant_identifier)
            except Tenant.DoesNotExist:
                try:
                    tenant = Tenant.objects.get(id=tenant_identifier)
                except (Tenant.DoesNotExist, ValueError):
                    raise InvalidToken({
                        'tenant': 'Invalid tenant identifier'
                    })
        else:
            # If no tenant provided, try to get user default tenant
            # This assumes your User model has a relation to Tenant
            # Adjust this logic based on your actual User model
            if hasattr(self.user, 'tenant'):
                tenant = self.user.tenant
            elif hasattr(self.user, 'tenants'):
                # If user belongs to multiple tenants, get the first active one
                tenant = self.user.tenants.filter(is_active=True).first()
        
        if not tenant:
            raise InvalidToken({
                'tenant': 'Tenant identification required. Please provide a tenant slug or ID.'
            })
        
        if not tenant.is_active:
            raise InvalidToken({
                'tenant': f'Tenant {tenant.slug} is not active'
            })
        
        # Attach tenant to user for token generation
        self.user._tenant_for_token = tenant
        
        return data


class TenantTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that does not require authentication.
    
    This view is accessible without authentication and generates
    JWT tokens with tenant claims based on username/password + tenant.
    
    POST /api/v1/auth/token/
    {
        "username": "user@example.com",
        "password": "password123",
        "tenant": "acme-corp"
    }
    
    Returns:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    
    serializer_class = TenantTokenObtainPairSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]  # Accept JSON and form data
