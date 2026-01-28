"""
Test Template API - Show available templates and query examples.

This script demonstrates:
1. Template presets in the database
2. ACME's custom template
3. How to use the API endpoints
"""

import os
import django
import sys
import json

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant, Template


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():
    print_section("DATABASE TEMPLATES")
    
    print("\nTemplate Presets (Public):")
    for template in Template.objects.filter(is_preset=True):
        print(f"\n  ID: {template.id}")
        print(f"  Name: {template.name}")
        print(f"  Category: {template.category}")
        print(f"  Tier: {template.tier}")
        print(f"  Description: {template.description}")
        print(f"  Tags: {', '.join(template.tags)}")
    
    print("\n\nCustom Templates (Tenant-Specific):")
    for template in Template.objects.filter(is_preset=False):
        print(f"\n  ID: {template.id}")
        print(f"  Name: {template.name}")
        print(f"  Tenant: {template.tenant.name}")
        print(f"  Base Preset: {template.base_preset.name}")
        print(f"  Has Overrides: {'Yes' if template.template_overrides else 'No'}")
    
    print_section("ACME TENANT CONFIGURATION")
    
    acme = Tenant.objects.get(slug='acme')
    print(f"\nTenant: {acme.name}")
    print(f"Active Template: {acme.template.name}")
    print(f"Template Type: {'Preset' if acme.template.is_preset else 'Custom'}")
    
    if not acme.template.is_preset:
        print(f"Inherits From: {acme.template.base_preset.name}")
        
        # Show what's overridden
        if acme.template.template_overrides:
            print("\nOverridden Sections:")
            if 'pages' in acme.template.template_overrides:
                for page_id, page_data in acme.template.template_overrides['pages'].items():
                    if 'sections' in page_data:
                        for section in page_data['sections']:
                            print(f"  • {section['type']} (ID: {section['id']})")
    
    print_section("QUERY EXAMPLES")
    
    print("\n1. Get all presets:")
    print("   Template.objects.filter(is_preset=True)")
    print(f"   Result: {Template.objects.filter(is_preset=True).count()} presets")
    
    print("\n2. Get landing page templates:")
    print("   Template.objects.filter(category='landing', is_preset=True)")
    print(f"   Result: {Template.objects.filter(category='landing', is_preset=True).count()} templates")
    
    print("\n3. Get free tier templates:")
    print("   Template.objects.filter(tier='free', is_preset=True)")
    print(f"   Result: {Template.objects.filter(tier='free', is_preset=True).count()} templates")
    
    print("\n4. Get tenant's custom templates:")
    print("   Template.objects.filter(tenant=acme, is_preset=False)")
    print(f"   Result: {Template.objects.filter(tenant=acme, is_preset=False).count()} templates")
    
    print("\n5. Get resolved template JSON:")
    print("   acme.template.get_resolved_template_json()")
    resolved = acme.template.get_resolved_template_json()
    print(f"   Result: Template with {len(resolved['pages']['home']['sections'])} sections")
    
    print("\n" + "=" * 80)
    print("API ENDPOINT SUMMARY")
    print("=" * 80)
    print("\nPublic Endpoints (no auth required):")
    print("  GET /api/tenants/templates/presets/")
    print("      → List all template presets")
    print("  GET /api/tenants/templates/by_category/?category=<category>")
    print("      → Filter presets by category (landing, marketing, blog, etc.)")
    print("  GET /api/tenants/templates/by_tier/?tier=<tier>")
    print("      → Filter presets by tier (free, premium, enterprise)")
    
    print("\nAuthenticated Endpoints (require tenant token):")
    print("  GET /api/tenants/templates/")
    print("      → List all templates (presets + tenant's custom templates)")
    print("  GET /api/tenants/templates/{id}/")
    print("      → Get specific template details")
    print("  POST /api/tenants/templates/")
    print("      → Create custom template")
    print("  PUT /api/tenants/templates/{id}/")
    print("      → Update custom template")
    print("  DELETE /api/tenants/templates/{id}/")
    print("      → Delete custom template")
    print("  POST /api/tenants/templates/{id}/clone/")
    print("      → Clone a preset to create custom template")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
