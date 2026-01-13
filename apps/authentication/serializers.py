"""
Serializers for API client authentication and token generation.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import APIClient, APIClientUsageLog
from .tokens import create_token_pair_for_api_client


class APIClientTokenObtainSerializer(serializers.Serializer):
    """
    Serializer for obtaining JWT tokens using API client credentials.
    
    Input: client_id + client_secret
    Output: access_token + refresh_token
    """
    
    client_id = serializers.CharField(
        required=True,
        help_text=_("API client ID")
    )
    
    client_secret = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text=_("API client secret")
    )
    
    def validate(self, attrs):
        """
        Validate client credentials and generate tokens.
        """
        client_id = attrs.get('client_id')
        client_secret = attrs.get('client_secret')
        
        # Try to fetch the API client
        try:
            api_client = APIClient.objects.select_related('tenant').get(
                client_id=client_id
            )
        except APIClient.DoesNotExist:
            self._log_failed_attempt(client_id, "Client not found")
            raise serializers.ValidationError({
                'detail': _("Invalid client credentials")
            })
        
        # Check if client is active
        if not api_client.is_active:
            self._log_failed_attempt(
                client_id, 
                "Client disabled",
                api_client=api_client
            )
            raise serializers.ValidationError({
                'detail': _("API client is disabled")
            })
        
        # Check if tenant is active
        if not api_client.tenant.is_active:
            self._log_failed_attempt(
                client_id,
                "Tenant inactive",
                api_client=api_client
            )
            raise serializers.ValidationError({
                'detail': _("Tenant is not active")
            })
        
        # Verify client secret (constant-time comparison)
        if not api_client.verify_client_secret(client_secret):
            self._log_failed_attempt(
                client_id,
                "Invalid secret",
                api_client=api_client
            )
            raise serializers.ValidationError({
                'detail': _("Invalid client credentials")
            })
        
        # Check IP whitelist if configured
        request = self.context.get('request')
        if request and api_client.allowed_ips:
            client_ip = self._get_client_ip(request)
            if not api_client.is_ip_allowed(client_ip):
                self._log_failed_attempt(
                    client_id,
                    f"IP not allowed: {client_ip}",
                    api_client=api_client,
                    ip_address=client_ip
                )
                raise serializers.ValidationError({
                    'detail': _("Access denied from this IP address")
                })
        
        # All checks passed - generate tokens
        tokens = create_token_pair_for_api_client(api_client)
        
        # Log successful authentication
        self._log_successful_attempt(api_client, request)
        
        # Record usage
        api_client.record_usage()
        
        # Store API client in context for use in response
        self.context['api_client'] = api_client
        
        return tokens
    
    def _get_client_ip(self, request):
        """
        Extract client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_failed_attempt(self, client_id, reason, api_client=None, ip_address=None):
        """
        Log a failed authentication attempt.
        """
        request = self.context.get('request')
        
        APIClientUsageLog.objects.create(
            api_client=api_client,
            client_id=client_id,
            success=False,
            failure_reason=reason,
            ip_address=ip_address or (self._get_client_ip(request) if request else None),
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        )
    
    def _log_successful_attempt(self, api_client, request):
        """
        Log a successful authentication attempt.
        """
        APIClientUsageLog.objects.create(
            api_client=api_client,
            client_id=api_client.client_id,
            success=True,
            ip_address=self._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        )


class APIClientRefreshSerializer(serializers.Serializer):
    """
    Serializer for refreshing access tokens using a refresh token.
    """
    
    refresh = serializers.CharField(
        required=True,
        help_text=_("Refresh token")
    )
    
    def validate(self, attrs):
        """
        Validate refresh token and generate new access token.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        refresh_token_str = attrs.get('refresh')
        
        try:
            # Decode and validate refresh token
            refresh_token = RefreshToken(refresh_token_str)
            
            # Extract client information from token
            client_id = refresh_token.get('client_id')
            token_version = refresh_token.get('token_version')
            
            if not client_id:
                raise serializers.ValidationError({
                    'detail': _("Invalid refresh token")
                })
            
            # Fetch API client
            try:
                api_client = APIClient.objects.select_related('tenant').get(
                    client_id=client_id
                )
            except APIClient.DoesNotExist:
                raise serializers.ValidationError({
                    'detail': _("Invalid refresh token")
                })
            
            # Verify client is still active
            if not api_client.is_active:
                raise serializers.ValidationError({
                    'detail': _("API client is disabled")
                })
            
            # Verify tenant is still active
            if not api_client.tenant.is_active:
                raise serializers.ValidationError({
                    'detail': _("Tenant is not active")
                })
            
            # Verify token version (for revocation support)
            if token_version != api_client.token_version:
                raise serializers.ValidationError({
                    'detail': _("Token has been revoked")
                })
            
            # Generate new access token
            from .tokens import APIClientAccessToken
            new_access_token = APIClientAccessToken.for_api_client(api_client)
            
            return {
                'access': str(new_access_token),
                'access_token_expires_at': new_access_token['exp'],
                'token_type': 'Bearer'
            }
            
        except TokenError as e:
            raise serializers.ValidationError({
                'detail': _("Invalid or expired refresh token")
            })


class APIClientSerializer(serializers.ModelSerializer):
    """
    Serializer for API Client model (read-only operations).
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_slug = serializers.CharField(source='tenant.slug', read_only=True)
    
    class Meta:
        model = APIClient
        fields = [
            'id', 'client_id', 'name', 'description',
            'tenant', 'tenant_name', 'tenant_slug',
            'is_active', 'roles', 'scopes', 'rate_limit',
            'allowed_ips', 'created_at', 'updated_at', 'last_used_at',
            'metadata'
        ]
        read_only_fields = [
            'id', 'client_id', 'created_at', 'updated_at', 'last_used_at'
        ]


class APIClientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new API clients.
    
    Returns the plaintext client_secret only once during creation.
    """
    
    client_secret = serializers.CharField(
        read_only=True,
        help_text=_("Generated client secret (shown only once)")
    )
    
    class Meta:
        model = APIClient
        fields = [
            'id', 'client_id', 'client_secret', 'name', 'description',
            'tenant', 'roles', 'scopes', 'rate_limit', 'allowed_ips',
            'metadata'
        ]
        read_only_fields = ['id', 'client_id', 'client_secret']
    
    def create(self, validated_data):
        """
        Create a new API client with generated credentials.
        """
        # Generate client_id and client_secret
        client_id = APIClient.generate_client_id()
        client_secret = APIClient.generate_client_secret()
        
        # Create the client
        api_client = APIClient.objects.create(
            client_id=client_id,
            **validated_data
        )
        
        # Hash and store the secret
        api_client.set_client_secret(client_secret)
        api_client.save(update_fields=['client_secret_hash'])
        
        # Attach plaintext secret to instance (only for response)
        api_client.client_secret = client_secret
        
        return api_client
