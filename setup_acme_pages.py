"""
Setup ACME tenant with proper page configurations in the template.

This updates the template's template_overrides to include page configurations
for /, /login, and /admin pages.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant

# Get ACME tenant
acme = Tenant.objects.get(slug='acme')

print(f"Setting up pages for: {acme.name}")
print(f"Template: {acme.template.name}")

# Define page configurations
pages_config = {
    '/': {
        'template': 'DashboardLayout',
        'slots': {
            'header': {
                'type': 'HeaderComposite',
                'props': {
                    'title': 'Welcome to ACME Corporation',
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
                    'subtitle': 'Welcome back to ACME'
                }
            },
            'main': {
                'type': 'Container',
                'props': {
                    'maxWidth': 'sm',
                    'children': [
                        {
                            'type': 'Card',
                            'props': {
                                'sx': {'p': 4, 'mt': 4},
                                'children': [
                                    {
                                        'type': 'Heading',
                                        'props': {'level': 2, 'children': 'Sign In'}
                                    },
                                    {
                                        'type': 'Stack',
                                        'props': {
                                            'spacing': 3,
                                            'sx': {'mt': 2},
                                            'children': [
                                                {
                                                    'type': 'Input',
                                                    'props': {
                                                        'label': 'Email',
                                                        'type': 'email',
                                                        'placeholder': 'your.email@acme.com',
                                                        'fullWidth': True
                                                    }
                                                },
                                                {
                                                    'type': 'Input',
                                                    'props': {
                                                        'label': 'Password',
                                                        'type': 'password',
                                                        'placeholder': '••••••••',
                                                        'fullWidth': True
                                                    }
                                                },
                                                {
                                                    'type': 'Button',
                                                    'props': {
                                                        'children': 'Sign In',
                                                        'variant': 'contained',
                                                        'color': 'primary',
                                                        'fullWidth': True,
                                                        'size': 'large'
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
                    'subtitle': 'Manage your ACME account'
                }
            },
            'sidebar': {
                'type': 'Navigation',
                'props': {
                    'items': [
                        {'label': 'Overview', 'href': '/admin', 'icon': 'Dashboard'},
                        {'label': 'Users', 'href': '/admin/users', 'icon': 'People'},
                        {'label': 'Settings', 'href': '/admin/settings', 'icon': 'Settings'},
                    ]
                }
            },
            'main': {
                'type': 'Container',
                'props': {
                    'children': [
                        {
                            'type': 'Heading',
                            'props': {'level': 1, 'children': 'Dashboard Overview'}
                        },
                        {
                            'type': 'Grid',
                            'props': {
                                'container': True,
                                'spacing': 3,
                                'sx': {'mt': 2},
                                'children': [
                                    {
                                        'type': 'Grid',
                                        'props': {
                                            'item': True,
                                            'xs': 12,
                                            'md': 4,
                                            'children': [
                                                {
                                                    'type': 'Card',
                                                    'props': {
                                                        'sx': {'p': 3},
                                                        'children': [
                                                            {'type': 'Heading', 'props': {'level': 3, 'children': 'Total Users'}},
                                                            {'type': 'Text', 'props': {'children': '1,247', 'variant': 'h3', 'sx': {'mt': 1}}}
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        'type': 'Grid',
                                        'props': {
                                            'item': True,
                                            'xs': 12,
                                            'md': 4,
                                            'children': [
                                                {
                                                    'type': 'Card',
                                                    'props': {
                                                        'sx': {'p': 3},
                                                        'children': [
                                                            {'type': 'Heading', 'props': {'level': 3, 'children': 'Active Sessions'}},
                                                            {'type': 'Text', 'props': {'children': '89', 'variant': 'h3', 'sx': {'mt': 1}}}
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        'type': 'Grid',
                                        'props': {
                                            'item': True,
                                            'xs': 12,
                                            'md': 4,
                                            'children': [
                                                {
                                                    'type': 'Card',
                                                    'props': {
                                                        'sx': {'p': 3},
                                                        'children': [
                                                            {'type': 'Heading', 'props': {'level': 3, 'children': 'Revenue'}},
                                                            {'type': 'Text', 'props': {'children': '$45,678', 'variant': 'h3', 'sx': {'mt': 1}}}
                                                        ]
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
    }
}

# Update the template's template_overrides with pages
if acme.template:
    # Get current overrides or create empty dict
    overrides = acme.template.template_overrides or {}
    
    # Update pages in overrides
    overrides['pages'] = pages_config
    
    # Save back to template
    acme.template.template_overrides = overrides
    acme.template.save()
    
    print(f"\n✅ Updated template overrides with {len(pages_config)} pages:")
    for path in pages_config.keys():
        print(f"   {path}")
    
    # Also update metadata.routes for the frontend routing
    routes_config = [
        {'path': '/', 'pagePath': '/', 'exact': True, 'title': 'Home'},
        {'path': '/login', 'pagePath': '/login', 'exact': True, 'title': 'Sign In'},
        {'path': '/admin', 'pagePath': '/admin', 'exact': True, 'title': 'Admin Dashboard'},
        {'path': '/about', 'pagePath': '/', 'exact': True, 'title': 'About Us'},
        {'path': '/products', 'pagePath': '/', 'exact': True, 'title': 'Products'},
    ]
    
    acme.metadata['routes'] = routes_config
    acme.save()
    
    print(f"\n✅ Updated tenant metadata with {len(routes_config)} routes")
    
    # Verify the configuration
    resolved = acme.template.get_resolved_template_json()
    print(f"\n✅ Template resolution successful")
    print(f"   Pages in resolved template: {list(resolved.get('pages', {}).keys())}")
    
else:
    print("\n❌ No template assigned to tenant!")

print("\n🎉 Setup complete!")
