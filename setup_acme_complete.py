"""
Setup complete ACME tenant configuration including theme and routes.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant

# Get ACME tenant
acme = Tenant.objects.get(slug='acme')

print(f"Configuring: {acme.name}")
print(f"Current theme: {acme.theme}")

# Set up theme configuration in metadata
if acme.theme:
    # Get the theme's resolved JSON
    theme_json = acme.theme.get_resolved_theme_json()
    
    # Store theme configuration in metadata so frontend can access it
    acme.metadata['theme'] = theme_json
    
    print(f"\n✅ Theme configuration saved to metadata")
    print(f"   Theme colors: {list(theme_json.get('colors', {}).keys())}")
else:
    print("\n⚠️  No theme assigned")

# Verify routes are set up
routes = acme.metadata.get('routes', [])
print(f"\n✅ Routes configured: {len(routes)}")
for route in routes:
    print(f"   {route['path']} → {route['pagePath']}")

# Save changes
acme.save()

print(f"\n✅ Configuration complete!")

# Print current state for verification
print(f"\n📊 Current Configuration:")
print(f"   Tenant: {acme.name} ({acme.slug})")
print(f"   Template: {acme.template.name if acme.template else 'None'}")
print(f"   Theme: {acme.theme.name if acme.theme else 'None'}")
print(f"   Routes: {len(routes)}")

if acme.template:
    resolved = acme.template.get_resolved_template_json()
    pages = resolved.get('pages', {})
    print(f"   Pages: {len(pages)} ({list(pages.keys())})")
