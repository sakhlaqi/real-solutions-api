"""
Management command to configure UI pages for tenants.

This command sets up the ui_config metadata for one or all tenants,
including page configurations for the dynamic routing system.

Usage:
    python manage.py configure_ui --slug=demo
    python manage.py configure_ui --all
    python manage.py configure_ui --slug=demo --template=marketing
"""

from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = 'Configure UI pages for tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Tenant slug to configure'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Configure all tenants'
        )
        parser.add_argument(
            '--template',
            type=str,
            default='default',
            choices=['default', 'marketing', 'saas', 'minimal'],
            help='UI template to use (default, marketing, saas, minimal)'
        )

    def handle(self, *args, **options):
        if options['all']:
            tenants = Tenant.objects.filter(is_active=True)
            self.stdout.write(f"Configuring {tenants.count()} tenants...")
        elif options['slug']:
            try:
                tenants = [Tenant.objects.get(slug=options['slug'])]
            except Tenant.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Tenant with slug '{options['slug']}' not found")
                )
                return
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --slug or --all')
            )
            return

        template_type = options['template']
        
        for tenant in tenants:
            self.configure_tenant(tenant, template_type)

    def configure_tenant(self, tenant, template_type):
        """Configure UI pages for a single tenant."""
        
        # Get page configurations based on template type
        pages_config = self.get_pages_config(tenant, template_type)
        
        # Update tenant metadata using update() to bypass validation
        metadata = tenant.metadata.copy()
        metadata['page_config'] = {
            'pages': pages_config,
            'version': '1.0.0',
        }
        
        # Use update() to avoid validation issues
        Tenant.objects.filter(id=tenant.id).update(metadata=metadata)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Configured {tenant.slug} with {template_type} template "
                f"({len(pages_config)} pages)"
            )
        )

    def get_pages_config(self, tenant, template_type):
        """Get page configurations based on template type."""
        
        if template_type == 'marketing':
            return self.get_marketing_pages(tenant)
        elif template_type == 'saas':
            return self.get_saas_pages(tenant)
        elif template_type == 'minimal':
            return self.get_minimal_pages(tenant)
        else:
            return self.get_default_pages(tenant)

    def get_default_pages(self, tenant):
        """Default landing page configuration."""
        return {
            '/': {
                'template': 'landing-page',
                'slots': {
                    'header': {
                        'component': 'Navbar',
                        'props': {
                            'logo': '/logo.png',
                            'links': [
                                {'label': 'Home', 'href': '/'},
                                {'label': 'About', 'href': '/about'},
                                {'label': 'Contact', 'href': '/contact'},
                            ]
                        }
                    },
                    'main': {
                        'component': 'Container',
                        'props': {
                            'children': [
                                {
                                    'component': 'Heading',
                                    'props': {
                                        'level': 1,
                                        'text': f'Welcome to {tenant.name}'
                                    }
                                },
                                {
                                    'component': 'Text',
                                    'props': {
                                        'text': 'Start building your application with our powerful platform.'
                                    }
                                }
                            ]
                        }
                    },
                    'footer': {
                        'component': 'Footer',
                        'props': {
                            'copyright': f'© 2026 {tenant.name}'
                        }
                    }
                }
            }
        }

    def get_marketing_pages(self, tenant):
        """Marketing-focused pages configuration."""
        return {
            '/': {
                'template': 'landing-page',
                'slots': {
                    'header': {
                        'component': 'Navbar',
                        'props': {
                            'logo': '/logo.png',
                            'variant': 'transparent',
                            'links': [
                                {'label': 'Features', 'href': '/features'},
                                {'label': 'Pricing', 'href': '/pricing'},
                                {'label': 'About', 'href': '/about'},
                                {'label': 'Contact', 'href': '/contact'},
                            ],
                            'actions': [
                                {'label': 'Sign In', 'href': '/login', 'variant': 'ghost'},
                                {'label': 'Get Started', 'href': '/signup', 'variant': 'primary'},
                            ]
                        }
                    },
                    'hero': {
                        'component': 'Hero',
                        'props': {
                            'title': f'Transform Your Business with {tenant.name}',
                            'subtitle': 'The complete platform for modern teams',
                            'primaryAction': {'label': 'Start Free Trial', 'href': '/signup'},
                            'secondaryAction': {'label': 'Watch Demo', 'href': '#demo'},
                        }
                    },
                    'features': {
                        'component': 'FeatureGrid',
                        'props': {
                            'title': 'Everything you need',
                            'features': [
                                {
                                    'icon': 'rocket',
                                    'title': 'Fast & Reliable',
                                    'description': 'Built for speed and performance'
                                },
                                {
                                    'icon': 'shield',
                                    'title': 'Secure',
                                    'description': 'Enterprise-grade security'
                                },
                                {
                                    'icon': 'chart',
                                    'title': 'Analytics',
                                    'description': 'Real-time insights'
                                },
                            ]
                        }
                    },
                    'footer': {
                        'component': 'Footer',
                        'props': {
                            'copyright': f'© 2026 {tenant.name}',
                            'links': [
                                {'label': 'Privacy', 'href': '/privacy'},
                                {'label': 'Terms', 'href': '/terms'},
                                {'label': 'Contact', 'href': '/contact'},
                            ]
                        }
                    }
                }
            },
            '/login': {
                'template': 'sign-in',
                'slots': {
                    'header': {
                        'component': 'Heading',
                        'props': {
                            'level': 2,
                            'text': f'Welcome back to {tenant.name}'
                        }
                    },
                    'footer': {
                        'component': 'Text',
                        'props': {
                            'text': "Don't have an account? Sign up",
                            'link': '/signup'
                        }
                    }
                }
            },
            '/signup': {
                'template': 'sign-up',
                'slots': {
                    'header': {
                        'component': 'Heading',
                        'props': {
                            'level': 2,
                            'text': f'Join {tenant.name} today'
                        }
                    },
                    'footer': {
                        'component': 'Text',
                        'props': {
                            'text': 'Already have an account? Sign in',
                            'link': '/login'
                        }
                    }
                }
            }
        }

    def get_saas_pages(self, tenant):
        """SaaS application pages configuration."""
        return {
            '/': {
                'template': 'landing-page',
                'slots': {
                    'header': {
                        'component': 'Navbar',
                        'props': {
                            'logo': '/logo.png',
                            'links': [
                                {'label': 'Dashboard', 'href': '/dashboard'},
                                {'label': 'Settings', 'href': '/settings'},
                            ]
                        }
                    },
                    'main': {
                        'component': 'Container',
                        'props': {
                            'children': [
                                {
                                    'component': 'Heading',
                                    'props': {'level': 1, 'text': f'{tenant.name} Dashboard'}
                                }
                            ]
                        }
                    }
                }
            },
            '/login': {
                'template': 'sign-in',
                'slots': {
                    'header': {
                        'component': 'Heading',
                        'props': {'level': 2, 'text': 'Sign in to your account'}
                    }
                }
            }
        }

    def get_minimal_pages(self, tenant):
        """Minimal pages configuration."""
        return {
            '/': {
                'template': 'landing-page',
                'slots': {
                    'main': {
                        'component': 'Container',
                        'props': {
                            'children': [
                                {
                                    'component': 'Heading',
                                    'props': {'level': 1, 'text': tenant.name}
                                }
                            ]
                        }
                    }
                }
            }
        }
