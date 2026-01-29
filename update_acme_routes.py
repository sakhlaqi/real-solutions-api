"""
Update ACME TenantRoute objects to properly map to page configurations.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant, TenantRoute

# Get ACME tenant
acme = Tenant.objects.get(slug='acme')

print(f"Updating routes for: {acme.name}\n")

# Define the correct route mappings
route_configs = [
    {
        'path': '/',
        'page_path': '/',
        'title': 'Home - ACME Corporation',
        'exact': True,
        'protected': False,
        'layout': 'DashboardLayout',
        'order': 0
    },
    {
        'path': '/login',
        'page_path': '/login',
        'title': 'Sign In - ACME Corporation',
        'exact': True,
        'protected': False,
        'layout': 'DashboardLayout',
        'order': 1
    },
    {
        'path': '/admin',
        'page_path': '/admin',
        'title': 'Admin Dashboard - ACME Corporation',
        'exact': True,
        'protected': True,
        'layout': 'DashboardLayout',
        'order': 2
    },
    {
        'path': '/about',
        'page_path': '/',
        'title': 'About Us - ACME Corporation',
        'exact': True,
        'protected': False,
        'layout': 'DashboardLayout',
        'order': 3
    },
    {
        'path': '/products',
        'page_path': '/',
        'title': 'Our Products - ACME Corporation',
        'exact': True,
        'protected': False,
        'layout': 'DashboardLayout',
        'order': 4
    },
]

# Delete existing routes
existing_routes = TenantRoute.objects.filter(tenant=acme)
print(f"Deleting {existing_routes.count()} existing routes...")
existing_routes.delete()

# Create new routes
print(f"Creating {len(route_configs)} new routes...\n")
for config in route_configs:
    route = TenantRoute.objects.create(
        tenant=acme,
        **config
    )
    print(f"✅ {route.path} → page: {route.page_path} (title: {route.title})")

print(f"\n🎉 Routes updated successfully!")

# Verify
print(f"\nVerification:")
routes = TenantRoute.objects.filter(tenant=acme).order_by('order')
print(f"Total routes: {routes.count()}")
for route in routes:
    print(f"  {route.path} → {route.page_path} (protected: {route.protected})")
