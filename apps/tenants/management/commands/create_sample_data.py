"""
Management command to create sample tenant data for testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.core.models import Project

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample tenant data for testing the frontend'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample tenant data...')
        
        # Create or update tenants
        acme, created = Tenant.objects.update_or_create(
            slug='acme',
            defaults={
                'name': 'ACME Corporation',
                'metadata': {
                    'branding': {
                        'name': 'ACME Corporation',
                        'tagline': 'Innovation at its finest',
                        'logo': {
                            'light': '/assets/acme-logo-light.png',
                            'dark': '/assets/acme-logo-dark.png'
                        },
                        'favicon': '/favicon-acme.ico'
                    },
                    'theme': {
                        'colors': {
                            'primary': '#2563eb',
                            'secondary': '#7c3aed',
                            'accent': '#06b6d4',
                            'background': '#ffffff',
                            'surface': '#f8f9fa',
                            'text': {
                                'primary': '#212529',
                                'secondary': '#6c757d',
                                'inverse': '#ffffff'
                            },
                            'error': '#dc3545',
                            'success': '#28a745',
                            'warning': '#ffc107'
                        },
                        'fonts': {
                            'primary': 'Inter, sans-serif',
                            'secondary': 'Georgia, serif',
                            'sizes': {
                                'xs': '0.75rem',
                                'sm': '0.875rem',
                                'base': '1rem',
                                'lg': '1.125rem',
                                'xl': '1.25rem',
                                '2xl': '1.5rem',
                                '3xl': '1.875rem'
                            }
                        },
                        'spacing': {
                            'xs': '0.25rem',
                            'sm': '0.5rem',
                            'md': '1rem',
                            'lg': '1.5rem',
                            'xl': '2rem',
                            '2xl': '3rem'
                        },
                        'borderRadius': {
                            'sm': '0.25rem',
                            'md': '0.5rem',
                            'lg': '1rem',
                            'full': '9999px'
                        },
                        'shadows': {
                            'sm': '0 1px 2px rgba(0,0,0,0.05)',
                            'md': '0 4px 6px rgba(0,0,0,0.1)',
                            'lg': '0 10px 15px rgba(0,0,0,0.1)'
                        }
                    },
                    'feature_flags': {
                        'enableNewDashboard': True,
                        'showBetaFeatures': False
                    },
                    'layout_preferences': {
                        'headerStyle': 'default',
                        'footerStyle': 'default'
                    },
                    'landing_page_sections': [
                        {
                            'id': 'hero-1',
                            'componentType': 'hero',
                            'order': 1,
                            'visible': True,
                            'props': {
                                'title': 'Welcome to ACME Corporation',
                                'subtitle': 'Your trusted partner in innovation and excellence',
                                'ctaText': 'Get Started Today',
                                'ctaLink': '/login',
                                'align': 'center'
                            }
                        },
                        {
                            'id': 'features-1',
                            'componentType': 'featureGrid',
                            'order': 2,
                            'visible': True,
                            'props': {
                                'title': 'Why Choose ACME',
                                'subtitle': 'We deliver excellence in everything we do',
                                'columns': 3,
                                'features': [
                                    {
                                        'id': 'f1',
                                        'icon': '🚀',
                                        'title': 'Fast Performance',
                                        'description': 'Lightning-fast load times and optimal user experience'
                                    },
                                    {
                                        'id': 'f2',
                                        'icon': '🔒',
                                        'title': 'Secure & Reliable',
                                        'description': 'Enterprise-grade security and 99.9% uptime'
                                    },
                                    {
                                        'id': 'f3',
                                        'icon': '💡',
                                        'title': 'Innovative Solutions',
                                        'description': 'Cutting-edge technology to solve your challenges'
                                    }
                                ]
                            }
                        },
                        {
                            'id': 'cta-1',
                            'componentType': 'ctaSection',
                            'order': 3,
                            'visible': True,
                            'props': {
                                'title': 'Ready to Get Started?',
                                'description': 'Join thousands of satisfied customers today',
                                'buttonText': 'Start Free Trial',
                                'buttonLink': '/login'
                            }
                        }
                    ]
                }
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created tenant: {acme.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated tenant: {acme.name}'))
        
        # Create or update demo tenant
        demo, created = Tenant.objects.update_or_create(
            slug='demo',
            defaults={
                'name': 'Demo Company',
                'metadata': {
                    'branding': {
                        'name': 'Demo Company',
                        'tagline': 'Building the future together',
                        'logo': {'light': '', 'dark': ''},
                        'favicon': ''
                    },
                    'theme': {
                        'colors': {
                            'primary': '#10b981',
                            'secondary': '#8b5cf6',
                            'accent': '#f59e0b',
                            'background': '#ffffff',
                            'surface': '#f9fafb',
                            'text': {
                                'primary': '#111827',
                                'secondary': '#6b7280',
                                'inverse': '#ffffff'
                            },
                            'error': '#ef4444',
                            'success': '#10b981',
                            'warning': '#f59e0b'
                        }
                    },
                    'landing_page_sections': []
                }
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created tenant: {demo.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated tenant: {demo.name}'))
        
        # Create test users
        acme_user, created = User.objects.get_or_create(
            username='admin@acme.com',
            defaults={
                'email': 'admin@acme.com',
                'first_name': 'Admin',
                'last_name': 'User',
            }
        )
        
        if created:
            acme_user.set_password('password123')
            acme_user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created user: {acme_user.email}'))
        else:
            self.stdout.write(f'  User {acme_user.email} already exists')
        
        # Create sample projects
        for i in range(1, 6):
            project, created = Project.objects.update_or_create(
                tenant=acme,
                name=f'Project {i}',
                defaults={
                    'description': f'Description for project {i}',
                    'status': ['active', 'completed', 'archived'][i % 3]
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created project: {project.name}')
            else:
                self.stdout.write(f'  ✓ Updated project: {project.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write('\nTest credentials:')
        self.stdout.write(f'  Email: admin@acme.com')
        self.stdout.write(f'  Password: password123')
        self.stdout.write(f'  Tenant: acme')
        self.stdout.write('\nFrontend URL:')
        self.stdout.write(f'  http://localhost:3000/?tenant=acme')
