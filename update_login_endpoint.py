#!/usr/bin/env python
"""Update ACME tenant login page configuration."""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/salmanakhlaqi/Public/projects/real-solutions/api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant
import json

def find_and_update_login_form(node):
    """Recursively find LoginForm component and update apiEndpoint."""
    if isinstance(node, dict):
        if node.get('type') == 'LoginForm':
            if 'props' not in node:
                node['props'] = {}
            node['props']['apiEndpoint'] = 'http://localhost:8000/api/v1/auth/login/'
            return True
        for key, value in node.items():
            if find_and_update_login_form(value):
                return True
    elif isinstance(node, list):
        for item in node:
            if find_and_update_login_form(item):
                return True
    return False

# Get ACME tenant
tenant = Tenant.objects.get(slug='acme')
pages = tenant.page_config.get('pages', {})
login_page = pages.get('/login', {})

# Update LoginForm
if find_and_update_login_form(login_page):
    pages['/login'] = login_page
    tenant.page_config['pages'] = pages
    tenant.save()
    print('✓ Updated /login page configuration with API endpoint')
    print(f'\nLoginForm now uses: http://localhost:8000/api/v1/auth/login/')
else:
    print('✗ LoginForm component not found in /login page')
