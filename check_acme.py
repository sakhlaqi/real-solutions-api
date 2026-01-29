#!/usr/bin/env python
"""Check ACME tenant configuration"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/Users/salmanakhlaqi/Public/projects/real-solutions/api')
django.setup()

from apps.tenants.models import Tenant
import json

tenant = Tenant.objects.filter(slug='acme').first()
if not tenant:
    print('ACME tenant not found!')
    sys.exit(1)

print(f'Tenant: {tenant.name}')
print(f'Template: {tenant.template}')
print(f'Theme: {tenant.theme}')

if tenant.template:
    template = tenant.template
    print(f'\nTemplate details:')
    print(f'  Name: {template.name}')
    print(f'  Is Preset: {template.is_preset}')
    print(f'  Base Preset: {template.base_preset}')
    
    resolved = template.get_resolved_template_json()
    print(f'\n  Resolved template keys: {list(resolved.keys())}')
    
    if 'pages' in resolved:
        pages = resolved['pages']
        print(f'  Pages: {json.dumps(pages, indent=4)}')
    else:
        print('  No pages in template!')
        
print(f'\nMetadata:')
print(f'  theme: {tenant.metadata.get("theme")}')
print(f'  routes: {tenant.metadata.get("routes")}')

print(f'\nRoutes ({tenant.routes_config.count()}):')
for route in tenant.routes_config.all():
    print(f'  {route.path} -> {route.page_path}')
