"""
Custom views for JWT token generation with tenant support and API client authentication.
"""

import threading
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    APIClientTokenObtainSerializer,
    APIClientRefreshSerializer
)
from .throttling import APIClientTokenThrottle, APIClientRefreshThrottle

User = get_user_model()

# Thread-local storage for tenant during token generation
_thread_locals = threading.local()


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that adds tenant claim to JWT token.
    Accepts both username and email for authentication.
    
    Expects:
    - username OR email: User's username or email address
    - password: User's password
    - tenant: Tenant slug or ID (optional, will use user's default tenant if not provided)
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username optional since we'll accept email too
        self.fields['username'].required = False
        # Add email field (optional)
        self.fields['email'] = self.fields['username'].__class__(
            required=False,
            allow_blank=False,
            help_text="User's email address (alternative to username)"
        )
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
        
        # Try to get tenant from thread-local storage (set in validate method)
        tenant = getattr(_thread_locals, 'current_tenant', None)
        
        # Fallback to user attribute if thread-local not set
        if not tenant:
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
        Accepts either username or email for authentication.
        """
        from apps.tenants.models import Tenant
        from django.contrib.auth import authenticate
        
        # Get credentials - accept either username or email
        username = attrs.get('username', '').strip()
        email = attrs.get('email', '').strip()
        password = attrs.get('password')
        
        # Must provide either username or email
        if not username and not email:
            raise InvalidToken({
                'username': 'Either username or email is required'
            })
        
        # If email is provided, try to find user by email
        authenticate_username = username
        if not username and email:
            try:
                user = User.objects.get(email=email)
                authenticate_username = user.username
            except User.DoesNotExist:
                raise InvalidToken({
                    'email': 'No user found with this email address'
                })
        elif username and '@' in username:
            # Username looks like an email, try to find by email first
            try:
                user = User.objects.get(email=username)
                authenticate_username = user.username
            except User.DoesNotExist:
                # Fall back to treating it as username
                authenticate_username = username
        
        # Update attrs with resolved username for parent validation
        attrs['username'] = authenticate_username
        
        # Get tenant from request data
        tenant_identifier = attrs.pop('tenant', None)
        # Remove email from attrs before calling super
        attrs.pop('email', None)
        
        # First, authenticate the user manually to get the user object
        from django.contrib.auth import authenticate as django_authenticate
        user = django_authenticate(
            self.context.get('request'),
            username=attrs.get('username'),
            password=attrs.get('password')
        )
        
        if user is None:
            raise InvalidToken({'detail': 'No active account found with the given credentials'})
        
        # Now resolve tenant before token generation
        from apps.tenants.models import Tenant
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
            # If no tenant provided, try to get user's default tenant
            if hasattr(user, 'tenant'):
                tenant = user.tenant
            elif hasattr(user, 'tenants'):
                tenant = user.tenants.filter(is_active=True).first()
        
        if not tenant:
            raise InvalidToken({
                'tenant': 'Tenant identification required. Please provide a tenant slug or ID.'
            })
        
        if not tenant.is_active:
            raise InvalidToken({
                'tenant': f'Tenant {tenant.slug} is not active'
            })
        
        # Store tenant in thread-local storage BEFORE calling super().validate()
        # This allows get_token() classmethod to access the tenant
        _thread_locals.current_tenant = tenant
        
        # Also attach tenant to user as fallback
        user._tenant_for_token = tenant
        self.user = user
        
        try:
            # Now call parent to generate tokens (which will use get_token)
            data = super().validate(attrs)
            
            return data
        finally:
            # Clean up thread-local storage
            if hasattr(_thread_locals, 'current_tenant'):
                delattr(_thread_locals, 'current_tenant')


class TenantTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that does not require authentication.
    
    This view is accessible without authentication and generates
    JWT tokens with tenant claims based on username/password + tenant.
    
    POST /api/v1/auth/token/
    OR /api/v1/auth/login/
    {
        "email": "user@example.com",  (or "username")
        "password": "password123",
        "tenant": "acme"  (optional, will use user's default tenant)
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


class UserRegisterView(APIView):
    """
    User registration endpoint.
    
    POST /api/v1/auth/register/
    {
        "email": "user@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "tenant_slug": "acme"
    }
    
    Returns:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": "...",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle user registration."""
        from apps.tenants.models import Tenant
        from rest_framework import serializers
        
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        tenant_slug = request.data.get('tenant_slug')
        
        # Validate required fields
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate tenant
        if not tenant_slug:
            return Response(
                {'error': 'Tenant slug is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
        except Tenant.DoesNotExist:
            return Response(
                {'error': 'Invalid tenant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(username=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        
        # Associate user with tenant (adjust based on your User model)
        if hasattr(user, 'tenant'):
            user.tenant = tenant
            user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        refresh['tenant'] = str(tenant.id)
        refresh['tenant_slug'] = tenant.slug
        refresh['email'] = user.email
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)


class UserLogoutView(APIView):
    """
    User logout endpoint.
    Blacklists the refresh token.
    
    POST /api/v1/auth/logout/
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle user logout."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(APIView):
    """
    Get current authenticated user information.
    
    GET /api/v1/auth/me/
    
    Returns:
    {
        "id": "...",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "tenant_id": "...",
        "tenant_slug": "acme"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user info."""
        user = request.user
        tenant = getattr(request, 'tenant', None)
        
        return Response({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'tenant_id': str(tenant.id) if tenant else None,
            'tenant_slug': tenant.slug if tenant else None,
        })
