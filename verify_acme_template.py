"""
Verify ACME template configuration and demonstrate template resolution.

This script shows how templates work:
1. Preset templates provide base structure
2. Custom templates inherit from presets
3. Overrides customize specific sections
4. Resolution merges preset + overrides
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


def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent))


def main():
    print("=" * 80)
    print("ACME Template Verification")
    print("=" * 80)
    
    # Get ACME tenant
    acme = Tenant.objects.get(slug='acme')
    print(f"\nTenant: {acme.name}")
    print(f"Active Template: {acme.template.name}")
    print(f"Template Type: {'Preset' if acme.template.is_preset else 'Custom'}")
    
    if not acme.template.is_preset:
        print(f"Base Preset: {acme.template.base_preset.name}")
    
    print("\n" + "-" * 80)
    print("PRESET TEMPLATE (Base Structure)")
    print("-" * 80)
    
    preset = acme.template.base_preset if not acme.template.is_preset else acme.template
    preset_hero = preset.template_json['pages']['home']['sections'][0]
    
    print(f"\nHero Section from '{preset.name}':")
    print(f"  Heading: {preset_hero['props']['heading']}")
    print(f"  Subheading: {preset_hero['props']['subheading']}")
    print(f"  CTA Text: {preset_hero['props']['ctaText']}")
    print(f"  Alignment: {preset_hero['props']['alignment']}")
    print(f"  Background: {preset_hero['props']['background']['type']}")
    
    if not acme.template.is_preset:
        print("\n" + "-" * 80)
        print("ACME OVERRIDES (Customizations)")
        print("-" * 80)
        
        overrides = acme.template.template_overrides
        if overrides and 'pages' in overrides:
            override_hero = overrides['pages']['home']['sections'][0]
            print(f"\nHero Section Overrides:")
            print(f"  Heading: {override_hero['props']['heading']}")
            print(f"  Subheading: {override_hero['props']['subheading']}")
            print(f"  CTA Text: {override_hero['props']['ctaText']}")
            print(f"  Alignment: {override_hero['props']['alignment']}")
            print(f"  Background: {override_hero['props']['background']['type']}")
        
    print("\n" + "-" * 80)
    print("RESOLVED TEMPLATE (Final Result)")
    print("-" * 80)
    
    resolved = acme.template.get_resolved_template_json()
    resolved_hero = resolved['pages']['home']['sections'][0]
    
    print(f"\nFinal Hero Section (Preset + Overrides Merged):")
    print(f"  Heading: {resolved_hero['props']['heading']}")
    print(f"  Subheading: {resolved_hero['props']['subheading']}")
    print(f"  CTA Text: {resolved_hero['props']['ctaText']}")
    print(f"  Alignment: {resolved_hero['props']['alignment']}")
    print(f"  Background: {resolved_hero['props']['background']['type']}")
    
    print("\n" + "-" * 80)
    print("ALL SECTIONS IN RESOLVED TEMPLATE")
    print("-" * 80)
    
    for idx, section in enumerate(resolved['pages']['home']['sections'], 1):
        print(f"\n{idx}. {section['type']} (ID: {section['id']})")
        if 'title' in section['props']:
            print(f"   Title: {section['props']['title']}")
        if 'heading' in section['props']:
            print(f"   Heading: {section['props']['heading']}")
    
    print("\n" + "=" * 80)
    print("DATABASE RECORDS")
    print("=" * 80)
    
    print(f"\nTotal Templates in DB: {Template.objects.count()}")
    print(f"  Presets: {Template.objects.filter(is_preset=True).count()}")
    print(f"  Custom: {Template.objects.filter(is_preset=False).count()}")
    
    print("\nAll Templates:")
    for template in Template.objects.all():
        template_type = "PRESET" if template.is_preset else "CUSTOM"
        tenant_info = f" (Tenant: {template.tenant.name})" if template.tenant else ""
        base_info = f" [Base: {template.base_preset.name}]" if template.base_preset else ""
        print(f"  [{template_type}] {template.name}{tenant_info}{base_info}")
    
    print("\n" + "=" * 80)
    print("✓ Verification Complete!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  • Preset templates are immutable and reusable")
    print("  • Custom templates inherit from presets")
    print("  • Overrides allow tenant-specific customization")
    print("  • Resolution merges preset + overrides at runtime")
    print("  • Templates behave exactly like themes")
    print("=" * 80)


if __name__ == '__main__':
    main()
