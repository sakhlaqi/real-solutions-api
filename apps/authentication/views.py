"""
Custom views for JWT token generation with tenant support and API client authentication.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    APIClientTokenObtainSerializer,
    APIClientRefreshSerializer
)
from .throttling import APIClientTokenThrottle, APIClientRefreshThrottle

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


class APIClientTokenObtainView(APIView):
    """
    API Client token issuance endpoint.
    
    Authenticates using client_id + client_secret and returns JWT tokens.
    Suitable for machine-to-machine and service account authentication.
    
    Features:
    - Secure secret verification (constant-time comparison)
    - Rate limiting to prevent brute-force attacks
    - Audit logging of authentication attempts
    - IP whitelist support
    - Token versioning for revocation
    
    POST /api/v1/auth/api-client/token/
    {
        "client_id": "client_a1b2c3d4e5f6",
        "client_secret": "your-secret-key"
    }
    
    Returns:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access_token_expires_at": 1234567890,
        "refresh_token_expires_at": 1234567890,
        "token_type": "Bearer"
    }
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [APIClientTokenThrottle]
    serializer_class = APIClientTokenObtainSerializer
    
    @extend_schema(
        request=APIClientTokenObtainSerializer,
        responses={
            200: OpenApiResponse(
                description="JWT tokens issued successfully"
            ),
            400: OpenApiResponse(
                description="Invalid credentials or validation error"
            ),
            429: OpenApiResponse(
                description="Rate limit exceeded"
            ),
        },
        tags=['Authentication - API Clients'],
        summary="Obtain JWT tokens using API client credentials",
        description=(
            "Exchange API client credentials (client_id + client_secret) "
            "for JWT access and refresh tokens. "
            "This endpoint is for machine-to-machine authentication."
        )
    )
    def post(self, request, *args, **kwargs):
        """
        Handle API client token requests.
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            # Return generic error message for security
            return Response(
                {'detail': 'Authentication failed'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class APIClientRefreshTokenView(APIView):
    """
    API Client token refresh endpoint.
    
    Exchange a refresh token for a new access token.
    
    POST /api/v1/auth/api-client/token/refresh/
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    
    Returns:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access_token_expires_at": 1234567890,
        "token_type": "Bearer"
    }
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [APIClientRefreshThrottle]
    serializer_class = APIClientRefreshSerializer
    
    @extend_schema(
        request=APIClientRefreshSerializer,
        responses={
            200: OpenApiResponse(
                description="New access token issued"
            ),
            400: OpenApiResponse(
                description="Invalid or expired refresh token"
            ),
            429: OpenApiResponse(
                description="Rate limit exceeded"
            ),
        },
        tags=['Authentication - API Clients'],
        summary="Refresh access token",
        description=(
            "Exchange a valid refresh token for a new access token. "
            "The refresh token remains valid and can be reused."
        )
    )
    def post(self, request, *args, **kwargs):
        """
        Handle token refresh requests.
        """
        serializer = self.serializer_class(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
