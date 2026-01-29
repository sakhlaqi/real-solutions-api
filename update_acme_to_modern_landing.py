#!/usr/bin/env python3
"""
Update ACME tenant to use the new Modern Landing preset v2.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant, Template

# Get ACME tenant and Modern Landing preset
acme = Tenant.objects.get(slug='acme')
modern_landing = Template.objects.get(is_preset=True, name='Modern Landing')

print(f'Updating {acme.name} to use {modern_landing.name} v{modern_landing.version}')

# Update ACME's template to use the new preset as base
if acme.template:
    # Update existing template to reference new base preset
    acme.template.base_preset = modern_landing
    acme.template.template_overrides = {}  # Clear overrides to use preset as-is
    acme.template.save()
    print(f'✅ Updated custom template to use {modern_landing.name} as base')
else:
    # If no template, assign the preset directly (not recommended, should use custom template)
    acme.template = modern_landing
    acme.save()
    print(f'✅ Assigned {modern_landing.name} directly to tenant')

# Verify the pages
resolved = acme.template.get_resolved_template_json()
pages = resolved.get('pages', {})

print(f'\n📄 Available pages:')
for path in pages.keys():
    page = pages[path]
    template_type = page.get('template', 'Unknown')
    print(f'  {path}: {template_type}')

print(f'\n✅ ACME tenant updated successfully!')
print(f'\n🌐 Access the pages at:')
print(f'  http://localhost:3001 (home page)')
print(f'  http://localhost:3001/login (authentication)')
print(f'  http://localhost:3001/admin (dashboard)')
