"""
Simulate the API response that the frontend receives for ACME tenant.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant
from apps.tenants.serializers import TenantConfigSerializer
import json

# Get ACME tenant
acme = Tenant.objects.get(slug='acme')

# Serialize using the same serializer the API uses
serializer = TenantConfigSerializer(acme)
data = serializer.data

print("=" * 80)
print("API RESPONSE FOR ACME TENANT")
print("=" * 80)

print(f"\nBasic Info:")
print(f"  Name: {data['name']}")
print(f"  Slug: {data['slug']}")

print(f"\nTheme:")
theme = data.get('theme')
if theme:
    print(f"  Has theme: Yes")
    print(f"  Theme keys: {list(theme.keys()) if isinstance(theme, dict) else type(theme)}")
else:
    print(f"  Has theme: No (will use defaults)")

print(f"\nRoutes:")
routes = data.get('routes', [])
print(f"  Count: {len(routes)}")
for route in routes:
    path = route.get('path') or route.get('pagePath')
    page = route.get('page_path') or route.get('pagePath')
    print(f"    {path} → {page}")

print(f"\nPage Config:")
page_config = data.get('page_config', {})
if page_config:
    pages = page_config.get('pages', {})
    if pages:
        print(f"  Pages count: {len(pages)}")
        for page_path in pages.keys():
            page = pages[page_path]
            template = page.get('template', 'Unknown')
            print(f"    {page_path}: {template}")
    else:
        print(f"  No pages configured")
else:
    print(f"  No page config")

print(f"\n" + "=" * 80)
print("FULL JSON RESPONSE:")
print("=" * 80)
print(json.dumps(data, indent=2, default=str))
