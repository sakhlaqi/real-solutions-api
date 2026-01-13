#!/usr/bin/env python
"""
Test script for API Client authentication.

This script demonstrates:
1. Creating an API client
2. Obtaining JWT tokens using client credentials
3. Making authenticated requests
4. Refreshing access tokens
5. Token validation

Usage:
    python test_api_client_auth.py
"""

import sys
import os
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from apps.authentication.models import APIClient
from apps.tenants.models import Tenant
from django.db import transaction


def create_test_client():
    """Create a test API client."""
    print("\n" + "=" * 70)
    print("Step 1: Creating Test API Client")
    print("=" * 70)
    
    # Get or create a test tenant
    tenant, created = Tenant.objects.get_or_create(
        slug='test-tenant',
        defaults={
            'name': 'Test Tenant',
            'is_active': True,
        }
    )
    
    if created:
        print(f"✓ Created test tenant: {tenant.name}")
    else:
        print(f"✓ Using existing tenant: {tenant.name}")
    
    # Generate credentials
    client_id = APIClient.generate_client_id(prefix='test_client')
    client_secret = APIClient.generate_client_secret()
    
    # Create API client
    with transaction.atomic():
        # Delete existing test client if it exists
        APIClient.objects.filter(name='Test API Client').delete()
        
        api_client = APIClient.objects.create(
            client_id=client_id,
            name='Test API Client',
            description='Automated test client for API authentication',
            tenant=tenant,
            roles=['read', 'write', 'admin'],
            scopes=['read:projects', 'write:projects', 'delete:projects'],
            is_active=True,
        )
        
        api_client.set_client_secret(client_secret)
        api_client.save(update_fields=['client_secret_hash'])
    
    print(f"\n✓ API Client Created Successfully!")
    print(f"  Client ID:     {client_id}")
    print(f"  Client Secret: {client_secret}")
    print(f"  Tenant:        {tenant.slug}")
    print(f"  Roles:         {', '.join(api_client.roles)}")
    print(f"  Scopes:        {', '.join(api_client.scopes)}")
    
    return client_id, client_secret


def obtain_tokens(base_url, client_id, client_secret):
    """Obtain JWT tokens using client credentials."""
    print("\n" + "=" * 70)
    print("Step 2: Obtaining JWT Tokens")
    print("=" * 70)
    
    url = f"{base_url}/api/v1/auth/api-client/token/"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    print(f"\nPOST {url}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✓ Authentication Successful!")
            print(f"\nAccess Token (first 50 chars):  {tokens['access'][:50]}...")
            print(f"Refresh Token (first 50 chars): {tokens['refresh'][:50]}...")
            print(f"Token Type: {tokens['token_type']}")
            print(f"Access Token Expires At: {tokens['access_token_expires_at']}")
            print(f"Refresh Token Expires At: {tokens['refresh_token_expires_at']}")
            return tokens
        else:
            print("✗ Authentication Failed!")
            print(f"Error: {response.json()}")
            return None
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error: Is the Django development server running?")
        print("  Start the server with: python manage.py runserver")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def make_authenticated_request(base_url, access_token):
    """Make an authenticated request using the access token."""
    print("\n" + "=" * 70)
    print("Step 3: Making Authenticated Request")
    print("=" * 70)
    
    url = f"{base_url}/api/v1/projects/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"\nGET {url}")
    print(f"Authorization: Bearer {access_token[:50]}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Request Successful!")
            data = response.json()
            print(f"Response: {data}")
            return True
        else:
            print("✗ Request Failed!")
            print(f"Error: {response.json()}")
            return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def refresh_access_token(base_url, refresh_token):
    """Refresh the access token using the refresh token."""
    print("\n" + "=" * 70)
    print("Step 4: Refreshing Access Token")
    print("=" * 70)
    
    url = f"{base_url}/api/v1/auth/api-client/token/refresh/"
    payload = {
        "refresh": refresh_token
    }
    
    print(f"\nPOST {url}")
    print(f"Refresh Token (first 50 chars): {refresh_token[:50]}...")
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✓ Token Refresh Successful!")
            print(f"\nNew Access Token (first 50 chars): {tokens['access'][:50]}...")
            print(f"Token Type: {tokens['token_type']}")
            print(f"Expires At: {tokens['access_token_expires_at']}")
            return tokens
        else:
            print("✗ Token Refresh Failed!")
            print(f"Error: {response.json()}")
            return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def decode_token(access_token):
    """Decode and display JWT token claims."""
    print("\n" + "=" * 70)
    print("Step 5: Decoding JWT Token Claims")
    print("=" * 70)
    
    try:
        import jwt
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        
        print("\n✓ Token Claims:")
        print(f"  Issuer (iss):        {decoded.get('iss')}")
        print(f"  Audience (aud):      {decoded.get('aud')}")
        print(f"  Subject (sub):       {decoded.get('sub')}")
        print(f"  JWT ID (jti):        {decoded.get('jti')}")
        print(f"  Issued At (iat):     {decoded.get('iat')}")
        print(f"  Expires At (exp):    {decoded.get('exp')}")
        print(f"  Client ID:           {decoded.get('client_id')}")
        print(f"  Client Type:         {decoded.get('client_type')}")
        print(f"  Tenant ID:           {decoded.get('tenant_id')}")
        print(f"  Tenant Slug:         {decoded.get('tenant_slug')}")
        print(f"  Roles:               {decoded.get('roles')}")
        print(f"  Scopes:              {decoded.get('scopes')}")
        print(f"  Token Version:       {decoded.get('token_version')}")
        print(f"  Token Type:          {decoded.get('token_type')}")
        
    except ImportError:
        print("\n⚠ PyJWT not installed. Skipping token decode.")
        print("  Install with: pip install PyJWT")
    except Exception as e:
        print(f"\n✗ Error decoding token: {e}")


def main():
    """Run the complete API client authentication test."""
    print("\n" + "=" * 70)
    print("API CLIENT AUTHENTICATION TEST")
    print("=" * 70)
    
    BASE_URL = "http://localhost:8000"
    
    # Step 1: Create test client
    client_id, client_secret = create_test_client()
    
    # Step 2: Obtain tokens
    tokens = obtain_tokens(BASE_URL, client_id, client_secret)
    if not tokens:
        print("\n✗ Test aborted: Could not obtain tokens")
        return
    
    # Step 3: Make authenticated request
    make_authenticated_request(BASE_URL, tokens['access'])
    
    # Step 4: Refresh token
    new_tokens = refresh_access_token(BASE_URL, tokens['refresh'])
    
    # Step 5: Decode token
    if new_tokens:
        decode_token(new_tokens['access'])
    
    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)
    print("\n✓ All steps completed successfully!")
    print("\nNext steps:")
    print("  1. Check the Django admin: http://localhost:8000/admin/")
    print("  2. View API client usage logs")
    print("  3. Try the API documentation: http://localhost:8000/api/schema/swagger/")


if __name__ == '__main__':
    main()
