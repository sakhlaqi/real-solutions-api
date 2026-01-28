"""
Configure ACME tenant to use a template preset with customizations.

This script demonstrates:
1. Creating a template preset (if not exists)
2. Assigning the preset to ACME tenant
3. Creating an override with ACME-specific customizations
"""

import os
import django
import sys
import uuid

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant, Template


def main():
    print("=" * 80)
    print("ACME Template Configuration")
    print("=" * 80)
    
    # Step 1: Get or create template preset
    print("\n[Step 1] Getting/Creating template preset...")
    
    preset_name = "Modern Landing"
    try:
        preset = Template.objects.get(name=preset_name, is_preset=True)
        print(f"✓ Found existing preset: {preset.name} (ID: {preset.id})")
    except Template.DoesNotExist:
        print(f"  Preset '{preset_name}' not found. Please run: python manage.py seed_template_presets")
        return
    
    # Step 2: Get ACME tenant
    print("\n[Step 2] Getting ACME tenant...")
    
    try:
        acme = Tenant.objects.get(slug='acme')
        print(f"✓ Found ACME tenant (ID: {acme.id})")
    except Tenant.DoesNotExist:
        print("  ERROR: ACME tenant not found. Please create it first.")
        return
    
    # Step 3: Assign preset to ACME (without overrides)
    print("\n[Step 3] Assigning preset to ACME tenant...")
    
    acme.template = preset
    acme.save()
    print(f"✓ ACME now using template: {preset.name}")
    
    # Step 4: Create ACME custom template with overrides
    print("\n[Step 4] Creating ACME custom template with overrides...")
    
    # Check if ACME already has a custom template
    existing_custom = Template.objects.filter(
        tenant=acme,
        base_preset=preset,
        is_preset=False
    ).first()
    
    if existing_custom:
        print(f"  Found existing custom template: {existing_custom.name}")
        custom_template = existing_custom
        update_existing = True
    else:
        custom_template = Template(
            tenant=acme,
            base_preset=preset,
            is_preset=False,
            category=preset.category,
            tier=preset.tier,
        )
        update_existing = False
    
    # Set custom properties
    custom_template.name = "ACME Modern Landing (Custom)"
    custom_template.version = "1.0.0"
    custom_template.description = "ACME customized version of Modern Landing template"
    custom_template.tags = ['acme', 'customized', 'landing']
    
    # For custom templates, template_json is required (can be minimal or inherit from preset)
    custom_template.template_json = {
        'meta': {
            'id': str(custom_template.id) if custom_template.id else str(uuid.uuid4()),
            'name': 'ACME Modern Landing (Custom)',
            'version': '1.0.0',
            'category': 'landing',
            'tier': 'free',
            'description': 'ACME customized version of Modern Landing template',
            'author': 'ACME Admin',
            'tags': ['acme', 'customized', 'landing'],
        }
    }
    
    # Create template overrides - customize the hero section
    custom_template.template_overrides = {
        'pages': {
            'home': {
                'sections': [
                    {
                        'id': 'hero',
                        'type': 'hero-simple',
                        'version': '1.0.0',
                        'props': {
                            # ACME-specific customizations
                            'heading': 'Welcome to ACME Corporation',
                            'subheading': 'Industry-leading solutions since 1985',
                            'ctaText': 'Explore Our Products',
                            'ctaLink': '/products',
                            'alignment': 'left',  # Changed from center to left
                            'background': {
                                'type': 'gradient',
                                'value': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'  # ACME brand colors
                            }
                        }
                    },
                    {
                        'id': 'features',
                        'type': 'features-grid',
                        'version': '1.0.0',
                        'props': {
                            'title': 'ACME Advantages',  # Customized title
                            'items': [
                                {
                                    'icon': 'rocket',
                                    'title': 'Innovation First',
                                    'description': 'Pioneering solutions that shape the industry'
                                },
                                {
                                    'icon': 'award',
                                    'title': '35+ Years Experience',
                                    'description': 'Trusted by Fortune 500 companies worldwide'
                                },
                                {
                                    'icon': 'users',
                                    'title': 'Expert Team',
                                    'description': 'Dedicated professionals committed to your success'
                                }
                            ]
                        }
                    },
                    {
                        'id': 'cta',
                        'type': 'cta-simple',
                        'version': '1.0.0',
                        'props': {
                            'heading': 'Partner with ACME Today',
                            'subheading': 'Join industry leaders who trust ACME',
                            'primaryButtonText': 'Request a Demo',
                            'primaryButtonLink': '/demo',
                            'secondaryButtonText': 'Contact Sales',
                            'secondaryButtonLink': '/contact-sales'
                        }
                    }
                ],
                'metadata': {
                    'metaTitle': 'ACME Corporation - Industry Leading Solutions',
                    'metaDescription': 'Discover ACME\'s innovative solutions trusted by Fortune 500 companies for over 35 years',
                }
            }
        },
        'metadata': {
            'customizedBy': 'ACME Admin',
            'customizedDate': '2026-01-27',
            'notes': 'Customized hero messaging, brand colors, and feature highlights'
        }
    }
    
    custom_template.save()
    
    if update_existing:
        print(f"✓ Updated existing custom template: {custom_template.name}")
    else:
        print(f"✓ Created new custom template: {custom_template.name}")
    
    # Step 5: Update ACME to use the custom template
    print("\n[Step 5] Updating ACME to use custom template...")
    
    acme.template = custom_template
    acme.save()
    print(f"✓ ACME now using custom template: {custom_template.name}")
    
    # Step 6: Verify resolution
    print("\n[Step 6] Verifying template resolution...")
    
    resolved = custom_template.get_resolved_template_json()
    
    print(f"✓ Template resolved successfully")
    print(f"  Base preset: {preset.name}")
    print(f"  Custom overrides applied: Yes")
    print(f"  Hero heading: {resolved['pages']['home']['sections'][0]['props']['heading']}")
    print(f"  Features title: {resolved['pages']['home']['sections'][1]['props']['title']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Preset Template:  {preset.name} (ID: {preset.id})")
    print(f"Custom Template:  {custom_template.name} (ID: {custom_template.id})")
    print(f"ACME Active:      {acme.template.name}")
    print(f"\nCustomizations:")
    print("  • Hero heading changed to 'Welcome to ACME Corporation'")
    print("  • Hero alignment changed from center to left")
    print("  • Brand gradient colors applied")
    print("  • Features customized with ACME-specific content")
    print("  • CTA buttons updated with ACME-specific text")
    print("\nTemplate Resolution:")
    print("  ✓ Base preset provides structure and defaults")
    print("  ✓ ACME overrides customize branding and messaging")
    print("  ✓ Resolved template merges both seamlessly")
    print("=" * 80)


if __name__ == '__main__':
    main()
