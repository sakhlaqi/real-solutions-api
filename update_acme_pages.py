"""
Update Acme tenant with login, signup, and admin pages
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant

# Get Acme tenant
acme = Tenant.objects.get(slug='acme')

# Update page configurations
page_config = {
    'pages': {
        '/': {
            'template': 'DashboardLayout',
            'slots': {
                'header': {
                    'type': 'HeaderComposite',
                    'props': {
                        'title': 'Welcome to Acme Corporation',
                        'subtitle': 'Innovation That Moves Mountains'
                    }
                },
                'main': {
                    'type': 'Container',
                    'props': {
                        'children': [
                            {
                                'type': 'Heading',
                                'props': {'level': 1, 'children': 'Welcome to ACME'}
                            },
                            {
                                'type': 'Text',
                                'props': {'children': 'Building the future, one solution at a time'}
                            },
                            {
                                'type': 'Stack',
                                'props': {
                                    'spacing': 2,
                                    'direction': 'row',
                                    'children': [
                                        {
                                            'type': 'Button',
                                            'props': {
                                                'children': 'Get Started',
                                                'variant': 'contained',
                                                'color': 'primary'
                                            }
                                        },
                                        {
                                            'type': 'Button',
                                            'props': {
                                                'children': 'Learn More',
                                                'variant': 'outlined'
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        '/login': {
            'template': 'DashboardLayout',
            'slots': {
                'header': {
                    'type': 'HeaderComposite',
                    'props': {
                        'title': 'Sign In',
                        'subtitle': 'Welcome back to Acme Corporation'
                    }
                },
                'main': {
                    'type': 'Container',
                    'props': {
                        'children': [
                            {
                                'type': 'Card',
                                'props': {
                                    'children': [
                                        {
                                            'type': 'Heading',
                                            'props': {'level': 2, 'children': 'Sign In to ACME'}
                                        },
                                        {
                                            'type': 'Stack',
                                            'props': {
                                                'spacing': 2,
                                                'children': [
                                                    {
                                                        'type': 'Input',
                                                        'props': {
                                                            'label': 'Email',
                                                            'type': 'email',
                                                            'placeholder': 'your.email@example.com'
                                                        }
                                                    },
                                                    {
                                                        'type': 'Input',
                                                        'props': {
                                                            'label': 'Password',
                                                            'type': 'password',
                                                            'placeholder': '••••••••'
                                                        }
                                                    },
                                                    {
                                                        'type': 'Button',
                                                        'props': {
                                                            'children': 'Sign In',
                                                            'variant': 'contained',
                                                            'color': 'primary',
                                                            'fullWidth': True
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        '/signup': {
            'template': 'DashboardLayout',
            'slots': {
                'header': {
                    'type': 'HeaderComposite',
                    'props': {
                        'title': 'Sign Up',
                        'subtitle': 'Create your Acme account'
                    }
                },
                'main': {
                    'type': 'Container',
                    'props': {
                        'children': [
                            {
                                'type': 'Card',
                                'props': {
                                    'children': [
                                        {
                                            'type': 'Heading',
                                            'props': {'level': 2, 'children': 'Create Account'}
                                        },
                                        {
                                            'type': 'Stack',
                                            'props': {
                                                'spacing': 2,
                                                'children': [
                                                    {
                                                        'type': 'Input',
                                                        'props': {
                                                            'label': 'Full Name',
                                                            'type': 'text',
                                                            'placeholder': 'John Doe'
                                                        }
                                                    },
                                                    {
                                                        'type': 'Input',
                                                        'props': {
                                                            'label': 'Email',
                                                            'type': 'email',
                                                            'placeholder': 'your.email@example.com'
                                                        }
                                                    },
                                                    {
                                                        'type': 'Input',
                                                        'props': {
                                                            'label': 'Password',
                                                            'type': 'password',
                                                            'placeholder': '••••••••'
                                                        }
                                                    },
                                                    {
                                                        'type': 'Button',
                                                        'props': {
                                                            'children': 'Sign Up',
                                                            'variant': 'contained',
                                                            'color': 'primary',
                                                            'fullWidth': True
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        '/admin': {
            'template': 'DashboardLayout',
            'slots': {
                'header': {
                    'type': 'HeaderComposite',
                    'props': {
                        'title': 'Admin Dashboard',
                        'subtitle': 'Manage your Acme Corporation account'
                    }
                },
                'sidebar': {
                    'type': 'SidebarComposite',
                    'props': {
                        'items': [
                            {'label': 'Dashboard', 'icon': 'dashboard', 'href': '/admin'},
                            {'label': 'Users', 'icon': 'people', 'href': '/admin/users'},
                            {'label': 'Settings', 'icon': 'settings', 'href': '/admin/settings'}
                        ]
                    }
                },
                'main': {
                    'type': 'Container',
                    'props': {
                        'children': [
                            {
                                'type': 'Heading',
                                'props': {'level': 1, 'children': 'Admin Dashboard'}
                            },
                            {
                                'type': 'Stack',
                                'props': {
                                    'spacing': 3,
                                    'direction': 'row',
                                    'children': [
                                        {
                                            'type': 'Card',
                                            'props': {
                                                'children': [
                                                    {'type': 'Heading', 'props': {'level': 3, 'children': 'Total Users'}},
                                                    {'type': 'Text', 'props': {'children': '1,234', 'variant': 'h4'}}
                                                ]
                                            }
                                        },
                                        {
                                            'type': 'Card',
                                            'props': {
                                                'children': [
                                                    {'type': 'Heading', 'props': {'level': 3, 'children': 'Active Sessions'}},
                                                    {'type': 'Text', 'props': {'children': '89', 'variant': 'h4'}}
                                                ]
                                            }
                                        },
                                        {
                                            'type': 'Card',
                                            'props': {
                                                'children': [
                                                    {'type': 'Heading', 'props': {'level': 3, 'children': 'Revenue'}},
                                                    {'type': 'Text', 'props': {'children': '$45,678', 'variant': 'h4'}}
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    },
    'version': '1.0.0'
}

# Update routes to match new pages
routes_config = [
    {'path': '/', 'pagePath': '/', 'exact': True, 'title': 'Home - Acme Corporation'},
    {'path': '/login', 'pagePath': '/login', 'exact': True, 'title': 'Sign In - Acme Corporation'},
    {'path': '/signup', 'pagePath': '/signup', 'exact': True, 'title': 'Sign Up - Acme Corporation'},
    {'path': '/admin', 'pagePath': '/admin', 'exact': True, 'title': 'Admin Dashboard - Acme Corporation'},
    {'path': '/about', 'pagePath': '/', 'exact': True, 'title': 'About Us - Acme Corporation'},
    {'path': '/products', 'pagePath': '/', 'exact': True, 'title': 'Our Products - Acme Corporation'},
]

# Update metadata
acme.metadata['page_config'] = page_config
acme.metadata['routes'] = routes_config
acme.save()

print('✓ Updated page configurations:')
for page_path in page_config['pages'].keys():
    print(f'  {page_path}')

print('\n✓ Updated routes:')
for route in routes_config:
    print(f"  {route['path']} → {route['pagePath']}")

print('\n✓ Configuration complete!')
