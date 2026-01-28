"""
Seed template presets into the database.

This management command creates official template presets that tenants can select.
Templates behave like themes - presets are immutable, tenants can fork and customize.
"""

from django.core.management.base import BaseCommand
from apps.tenants.models import Template
import uuid


class Command(BaseCommand):
    help = 'Seed template presets into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding template presets...'))

        # Landing Page Template Preset
        landing_template_id = str(uuid.uuid4())
        landing_template, created = Template.objects.get_or_create(
            name='Modern Landing',
            defaults={
                'id': landing_template_id,
                'version': '1.0.0',
                'is_preset': True,
                'category': 'landing',
                'tier': 'free',
                'description': 'Modern landing page with hero, features, and CTA sections',
                'preview_image': '/templates/modern-landing.jpg',
                'tags': ['modern', 'clean', 'responsive', 'hero', 'features'],
                'template_json': {
                    'meta': {
                        'id': landing_template_id,
                        'name': 'Modern Landing',
                        'version': '1.0.0',
                        'category': 'landing',
                        'tier': 'free',
                        'description': 'Modern landing page with hero, features, and CTA sections',
                        'author': 'Real Solutions',
                        'tags': ['modern', 'clean', 'responsive'],
                    },
                    'pages': {
                        'home': {
                            'id': 'home',
                            'title': 'Home',
                            'description': 'Landing page home',
                            'layout': {
                                'type': 'landing-layout',
                                'version': '1.0.0',
                                'props': {
                                    'fullWidth': True,
                                }
                            },
                            'sections': [
                                {
                                    'id': 'hero',
                                    'type': 'hero-simple',
                                    'version': '1.0.0',
                                    'props': {
                                        'heading': 'Transform Your Business',
                                        'subheading': 'Discover cutting-edge solutions tailored to your needs',
                                        'ctaText': 'Get Started',
                                        'ctaLink': '#features',
                                        'alignment': 'center',
                                        'background': {
                                            'type': 'gradient',
                                            'value': 'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 90%), transparent)'
                                        }
                                    }
                                },
                                {
                                    'id': 'features',
                                    'type': 'features-grid',
                                    'version': '1.0.0',
                                    'props': {
                                        'title': 'Why Choose Us',
                                        'items': [
                                            {
                                                'icon': 'rocket',
                                                'title': 'Fast Performance',
                                                'description': 'Lightning-fast load times and optimal performance'
                                            },
                                            {
                                                'icon': 'shield',
                                                'title': 'Secure & Reliable',
                                                'description': 'Enterprise-grade security and 99.9% uptime'
                                            },
                                            {
                                                'icon': 'support',
                                                'title': '24/7 Support',
                                                'description': 'Round-the-clock customer support whenever you need it'
                                            }
                                        ]
                                    }
                                },
                                {
                                    'id': 'cta',
                                    'type': 'cta-simple',
                                    'version': '1.0.0',
                                    'props': {
                                        'heading': 'Ready to Get Started?',
                                        'subheading': 'Join thousands of satisfied customers today',
                                        'primaryButtonText': 'Sign Up Now',
                                        'primaryButtonLink': '/signup',
                                        'secondaryButtonText': 'Learn More',
                                        'secondaryButtonLink': '/about'
                                    }
                                }
                            ],
                            'metadata': {
                                'metaTitle': 'Welcome - Modern Landing',
                                'metaDescription': 'Transform your business with our cutting-edge solutions',
                            }
                        }
                    },
                    'theme_preset_id': None,  # Will be set when linking to a theme
                    'metadata': {
                        'industry': 'SaaS',
                        'useCases': ['Product Launch', 'Lead Generation', 'Brand Awareness'],
                        'demoUrl': 'https://example.com/demo/modern-landing',
                    }
                }
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created template preset: {landing_template.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'  Template preset already exists: {landing_template.name}'))

        # Marketing Page Template Preset
        marketing_template_id = str(uuid.uuid4())
        marketing_template, created = Template.objects.get_or_create(
            name='Professional Marketing',
            defaults={
                'id': marketing_template_id,
                'version': '1.0.0',
                'is_preset': True,
                'category': 'marketing',
                'tier': 'premium',
                'description': 'Professional marketing page with advanced features',
                'preview_image': '/templates/professional-marketing.jpg',
                'tags': ['professional', 'marketing', 'conversion', 'testimonials'],
                'template_json': {
                    'meta': {
                        'id': marketing_template_id,
                        'name': 'Professional Marketing',
                        'version': '1.0.0',
                        'category': 'marketing',
                        'tier': 'premium',
                        'description': 'Professional marketing page with advanced features',
                        'author': 'Real Solutions',
                        'tags': ['professional', 'marketing', 'conversion'],
                    },
                    'pages': {
                        'home': {
                            'id': 'home',
                            'title': 'Home',
                            'description': 'Marketing home page',
                            'layout': {
                                'type': 'marketing-layout',
                                'version': '1.0.0',
                            },
                            'sections': [
                                {
                                    'id': 'hero',
                                    'type': 'hero-with-image',
                                    'version': '1.0.0',
                                    'props': {
                                        'heading': 'Grow Your Business',
                                        'subheading': 'Professional solutions for modern companies',
                                        'ctaText': 'Get Started',
                                        'ctaLink': '/contact',
                                        'imageUrl': '/images/hero-business.jpg'
                                    }
                                },
                                {
                                    'id': 'stats',
                                    'type': 'stats-grid',
                                    'version': '1.0.0',
                                    'props': {
                                        'items': [
                                            {'label': 'Customers', 'value': '10,000+'},
                                            {'label': 'Success Rate', 'value': '99%'},
                                            {'label': 'Countries', 'value': '50+'},
                                            {'label': 'Awards', 'value': '25+'}
                                        ]
                                    }
                                },
                                {
                                    'id': 'testimonials',
                                    'type': 'testimonials-carousel',
                                    'version': '1.0.0',
                                    'props': {
                                        'title': 'What Our Clients Say',
                                        'items': [
                                            {
                                                'quote': 'Absolutely game-changing for our business!',
                                                'author': 'Sarah Johnson',
                                                'role': 'CEO, TechCorp'
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created template preset: {marketing_template.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'  Template preset already exists: {marketing_template.name}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Template preset seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'  Total presets: {Template.objects.filter(is_preset=True).count()}'))
