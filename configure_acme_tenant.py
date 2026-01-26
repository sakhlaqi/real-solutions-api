"""
Acme Corporation - Complete UI Configuration Setup Example

This script demonstrates how to configure a tenant (Acme Corporation) 
with a full UI configuration including routes and page templates.

Run this script to set up Acme tenant:
    python manage.py shell < configure_acme_tenant.py

Or run directly in Django shell:
    python manage.py shell
    >>> exec(open('configure_acme_tenant.py').read())
"""

from apps.tenants.models import Tenant

# Get or create Acme tenant
acme, created = Tenant.objects.get_or_create(
    slug='acme',
    defaults={
        'name': 'Acme Corporation',
        'is_active': True,
    }
)

if created:
    print("✓ Created new Acme Corporation tenant")
else:
    print("✓ Found existing Acme Corporation tenant")

# Configure routes
routes_config = [
    {
        'path': '/',
        'pagePath': '/',
        'exact': True,
        'title': 'Home - Acme Corporation',
    },
    {
        'path': '/login',
        'pagePath': '/login',
        'exact': True,
        'title': 'Sign In - Acme Corporation',
    },
    {
        'path': '/signup',
        'pagePath': '/signup',
        'exact': True,
        'title': 'Sign Up - Acme Corporation',
    },
    {
        'path': '/admin',
        'pagePath': '/admin',
        'exact': True,
        'title': 'Admin Dashboard - Acme Corporation',
    },
    {
        'path': '/about',
        'pagePath': '/',
        'exact': True,
        'title': 'About Us - Acme Corporation',
    },
    {
        'path': '/products',
        'pagePath': '/',
        'exact': True,
        'title': 'Our Products - Acme Corporation',
    },
]

# Configure page config
page_config = {
    'pages': {
        '/': {
            'template': 'landing-page',
            'slots': {
                'header': {
                    'type': 'Navbar',
                    'props': {
                        'logo': '/acme-logo.png',
                        'variant': 'transparent',
                        'sticky': True,
                        'links': [
                            {'label': 'Home', 'href': '/'},
                            {'label': 'Products', 'href': '/products'},
                            {'label': 'About', 'href': '/about'},
                            {'label': 'Contact', 'href': '/contact'},
                        ],
                        'actions': [
                            {
                                'label': 'Sign In',
                                'href': '/login',
                                'variant': 'ghost',
                            },
                            {
                                'label': 'Get Started',
                                'href': '/signup',
                                'variant': 'primary',
                            },
                        ],
                    },
                },
                'hero': {
                    'type': 'Hero',
                    'props': {
                        'title': 'Innovation That Moves Mountains',
                        'subtitle': 'Acme Corporation - Building the future, one solution at a time',
                        'backgroundImage': '/hero-bg.jpg',
                        'primaryAction': {
                            'label': 'Explore Products',
                            'href': '/products',
                        },
                        'secondaryAction': {
                            'label': 'Watch Demo',
                            'href': '#demo',
                        },
                    },
                },
                'features': {
                    'type': 'FeatureGrid',
                    'props': {
                        'title': 'Why Choose Acme?',
                        'subtitle': 'Industry-leading solutions trusted by thousands',
                        'columns': 3,
                        'features': [
                            {
                                'icon': 'rocket',
                                'title': 'Lightning Fast',
                                'description': 'Optimized performance for all your needs',
                            },
                            {
                                'icon': 'shield',
                                'title': 'Secure & Reliable',
                                'description': 'Enterprise-grade security and 99.9% uptime',
                            },
                            {
                                'icon': 'globe',
                                'title': 'Global Scale',
                                'description': 'Serving customers in over 150 countries',
                            },
                            {
                                'icon': 'heart',
                                'title': 'Customer First',
                                'description': '24/7 support and dedicated success team',
                            },
                            {
                                'icon': 'code',
                                'title': 'Developer Friendly',
                                'description': 'Comprehensive APIs and documentation',
                            },
                            {
                                'icon': 'chart',
                                'title': 'Real-time Analytics',
                                'description': 'Monitor and optimize your operations',
                            },
                        ],
                    },
                },
                'testimonials': {
                    'type': 'Testimonials',
                    'props': {
                        'title': 'Loved by Industry Leaders',
                        'testimonials': [
                            {
                                'quote': 'Acme transformed how we do business. Incredible results!',
                                'author': 'Jane Doe',
                                'role': 'CEO, TechCorp',
                                'avatar': '/testimonial-1.jpg',
                            },
                            {
                                'quote': 'Best decision we made this year. Highly recommend!',
                                'author': 'John Smith',
                                'role': 'CTO, StartupXYZ',
                                'avatar': '/testimonial-2.jpg',
                            },
                        ],
                    },
                },
                'cta': {
                    'type': 'CallToAction',
                    'props': {
                        'title': 'Ready to Get Started?',
                        'subtitle': 'Join thousands of satisfied customers today',
                        'primaryAction': {
                            'label': 'Start Free Trial',
                            'href': '/signup',
                        },
                        'secondaryAction': {
                            'label': 'Schedule a Demo',
                            'href': '/contact',
                        },
                    },
                },
                'footer': {
                    'component': 'Footer',
                    'props': {
                        'logo': '/acme-logo-white.png',
                        'copyright': '© 2026 Acme Corporation. All rights reserved.',
                        'sections': [
                            {
                                'title': 'Product',
                                'links': [
                                    {'label': 'Features', 'href': '/features'},
                                    {'label': 'Pricing', 'href': '/pricing'},
                                    {'label': 'Updates', 'href': '/updates'},
                                ],
                            },
                            {
                                'title': 'Company',
                                'links': [
                                    {'label': 'About', 'href': '/about'},
                                    {'label': 'Careers', 'href': '/careers'},
                                    {'label': 'Blog', 'href': '/blog'},
                                ],
                            },
                            {
                                'title': 'Legal',
                                'links': [
                                    {'label': 'Privacy', 'href': '/privacy'},
                                    {'label': 'Terms', 'href': '/terms'},
                                    {'label': 'Security', 'href': '/security'},
                                ],
                            },
                        ],
                        'social': [
                            {'platform': 'twitter', 'url': 'https://twitter.com/acmecorp'},
                            {'platform': 'linkedin', 'url': 'https://linkedin.com/company/acme'},
                            {'platform': 'github', 'url': 'https://github.com/acmecorp'},
                        ],
                    },
                },
            },
        },
        '/login': {
            'template': 'sign-in',
            'slots': {
                'header': {
                    'type': 'Heading',
                    'props': {
                        'level': 2,
                        'text': 'Welcome back to Acme',
                    },
                },
                'subheader': {
                    'component': 'Text',
                    'props': {
                        'text': 'Sign in to access your account',
                        'align': 'center',
                        'variant': 'muted',
                    },
                },
                'social': {
                    'component': 'SocialLogins',
                    'props': {
                        'providers': ['google', 'github'],
                    },
                },
                'footer': {
                    'component': 'Text',
                    'props': {
                        'text': "Don't have an account?",
                        'link': {
                            'label': 'Sign up',
                            'href': '/signup',
                        },
                    },
                },
            },
        },
        '/signup': {
            'template': 'sign-up',
            'slots': {
                'header': {
                    'type': 'Heading',
                    'props': {
                        'level': 2,
                        'text': 'Create your Acme account',
                    },
                },
                'subheader': {
                    'component': 'Text',
                    'props': {
                        'text': 'Get started with a free 14-day trial',
                        'align': 'center',
                        'variant': 'muted',
                    },
                },
                'social': {
                    'component': 'SocialLogins',
                    'props': {
                        'providers': ['google', 'github'],
                    },
                },
                'footer': {
                    'component': 'Text',
                    'props': {
                        'text': 'Already have an account?',
                        'link': {
                            'label': 'Sign in',
                            'href': '/login',
                        },
                    },
                },
            },
        },
        '/admin': {
            'template': 'dashboard',
            'slots': {
                'header': {
                    'type': 'Navbar',
                    'props': {
                        'logo': '/acme-logo.png',
                        'variant': 'admin',
                        'links': [
                            {'label': 'Dashboard', 'href': '/admin'},
                            {'label': 'Users', 'href': '/admin/users'},
                            {'label': 'Settings', 'href': '/admin/settings'},
                        ],
                    },
                },
                'main': {
                    'type': 'Container',
                    'props': {
                        'children': [
                            {
                                'type': 'Heading',
                                'props': {'level': 1, 'text': 'Admin Dashboard'}
                            },
                            {
                                'type': 'Grid',
                                'props': {
                                    'columns': 3,
                                    'gap': 'md',
                                    'children': [
                                        {
                                            'type': 'Card',
                                            'props': {
                                                'children': [
                                                    {'type': 'Heading', 'props': {'level': 3, 'text': 'Total Users'}},
                                                    {'type': 'Text', 'props': {'text': '1,234'}}
                                                ]
                                            }
                                        },
                                        {
                                            'type': 'Card',
                                            'props': {
                                                'children': [
                                                    {'type': 'Heading', 'props': {'level': 3, 'text': 'Active Sessions'}},
                                                    {'type': 'Text', 'props': {'text': '89'}}
                                                ]
                                            }
                                        },
                                        {
                                            'type': 'Card',
                                            'props': {
                                                'children': [
                                                    {'type': 'Heading', 'props': {'level': 3, 'text': 'Revenue'}},
                                                    {'type': 'Text', 'props': {'text': '$45,678'}}
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                },
                'footer': {
                    'type': 'Footer',
                    'props': {'copyright': '© 2026 ACME Corporation - Admin'}
                },
            },
        },
        '/about': {
            'template': 'marketing-page',
            'slots': {
                'header': {
                    'type': 'Navbar',
                    'props': {
                        'logo': '/acme-logo.png',
                        'links': [
                            {'label': 'Home', 'href': '/'},
                            {'label': 'Products', 'href': '/products'},
                            {'label': 'About', 'href': '/about'},
                        ],
                    },
                },
                'hero': {
                    'component': 'PageHeader',
                    'props': {
                        'title': 'About Acme Corporation',
                        'subtitle': 'Innovating since 1949',
                    },
                },
                'content': {
                    'component': 'RichText',
                    'props': {
                        'content': '''
                        <h2>Our Story</h2>
                        <p>Founded in 1949, Acme Corporation has been at the forefront of innovation...</p>
                        
                        <h2>Our Mission</h2>
                        <p>To deliver cutting-edge solutions that empower businesses worldwide...</p>
                        
                        <h2>Our Values</h2>
                        <ul>
                            <li>Innovation - Always pushing boundaries</li>
                            <li>Integrity - Doing the right thing</li>
                            <li>Excellence - Never settling for good enough</li>
                        </ul>
                        ''',
                    },
                },
                'footer': {
                    'component': 'Footer',
                    'props': {
                        'copyright': '© 2026 Acme Corporation',
                    },
                },
            },
        },
        '/products': {
            'template': 'marketing-page',
            'slots': {
                'header': {
                    'component': 'Navbar',
                    'props': {
                        'logo': '/acme-logo.png',
                        'links': [
                            {'label': 'Home', 'href': '/'},
                            {'label': 'Products', 'href': '/products'},
                            {'label': 'About', 'href': '/about'},
                        ],
                    },
                },
                'hero': {
                    'component': 'PageHeader',
                    'props': {
                        'title': 'Our Products',
                        'subtitle': 'Solutions for every need',
                    },
                },
                'content': {
                    'component': 'ProductGrid',
                    'props': {
                        'products': [
                            {
                                'name': 'Acme Pro',
                                'description': 'Our flagship enterprise solution',
                                'image': '/product-pro.jpg',
                                'link': '/products/pro',
                            },
                            {
                                'name': 'Acme Starter',
                                'description': 'Perfect for small teams',
                                'image': '/product-starter.jpg',
                                'link': '/products/starter',
                            },
                            {
                                'name': 'Acme Enterprise',
                                'description': 'For large organizations',
                                'image': '/product-enterprise.jpg',
                                'link': '/products/enterprise',
                            },
                        ],
                    },
                },
                'footer': {
                    'component': 'Footer',
                    'props': {
                        'copyright': '© 2026 Acme Corporation',
                    },
                },
            },
        },
    },
    'version': '1.0.0',
}

# Update tenant metadata
metadata = acme.metadata.copy()
metadata['routes'] = routes_config
metadata['page_config'] = page_config

# Use update to bypass validation
Tenant.objects.filter(id=acme.id).update(metadata=metadata)

print("✓ Configured routes (5 routes)")
print("✓ Configured UI pages (5 pages)")
print(f"\nAcme Corporation is ready!")
print(f"\nTest the endpoint:")
print(f"  curl http://localhost:8000/api/v1/tenants/acme/ui-config/")
print(f"\nView in presentation:")
print(f"  http://localhost:3001/?tenant=acme")
