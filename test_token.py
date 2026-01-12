#!/usr/bin/env python
"""Test script for token endpoint"""
import requests
import json
import sys

try:
    response = requests.post(
        'http://127.0.0.1:8001/api/v1/auth/token/',
        headers={'Content-Type': 'application/json'},
        json={
            'username': 'acme_user',
            'password': 'testpass123',
            'tenant': 'acme'
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
