#!/usr/bin/env python
"""
Seed Template Presets
Creates official template presets for common use cases.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Template


def seed_template_presets():
    """Create official template presets."""
    presets = [
        {
            'name': 'Modern Landing',
            'version': '1.0.0',
            'category': 'landing',
            'tier': 'free',
            'description': 'Modern landing page with hero, features, and CTA sections',
            'template_json': {
                'meta': {
                    'id': 'modern-landing',
                    'name': 'Modern Landing',
                    'version': '1.0.0',
                    'category': 'landing',
                    'tier': 'free'
                },
                'pages': {
                    'home': {
                        'id': 'home',
                        'title': 'Home',
                        'description': 'Landing page',
                        'layout': {
                            'type': 'default-layout',
                            'version': '1.0.0'
                        },
                        'sections': [
                            {
                                'id': 'hero',
                                'type': 'hero-simple',
                                'version': '1.0.0',
                                'props': {
                                    'heading': 'Welcome to Our Platform',
                                    'subheading': 'Build amazing things together',
                                    'alignment': 'center'
                                }
                            },
                            {
                                'id': 'features',
                                'type': 'features-grid',
                                'version': '1.0.0',
                                'props': {
                                    'title': 'Our Features',
                                    'columns': 3
                                }
                            }
                        ],
                        'metadata': {
                            'metaTitle': 'Home',
                            'metaDescription': 'Welcome to our platform'
                        }
                    }
                },
                'version': '1.0.0'
            }
        },
    ]
    
    created = []
    for preset_data in presets:
        preset, created_flag = Template.objects.get_or_create(
            name=preset_data['name'],
            defaults={
                **preset_data,
                'is_preset': True,
                'tenant': None,
                'base_preset': None,
            }
        )
        if created_flag:
            created.append(preset.name)
            print(f"✓ Created preset: {preset.name}")
        else:
            print(f"  Preset already exists: {preset.name}")
    
    return created


if __name__ == '__main__':
    print("=" * 80)
    print("Seeding Template Presets")
    print("=" * 80)
    
    created = seed_template_presets()
    
    print("\n" + "=" * 80)
    print(f"Summary: Created {len(created)} new presets")
    print("=" * 80)
