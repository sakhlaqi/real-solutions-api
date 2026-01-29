#!/usr/bin/env python3
"""
Update Modern Landing preset template with proper template/slots architecture.
Creates pages for /, /login, and /admin using the current JSON-driven UI approach.
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Template

# Find the Modern Landing preset
preset = Template.objects.filter(is_preset=True, name='Modern Landing').first()

if not preset:
    print('❌ Modern Landing preset not found!')
    exit(1)

print(f'Updating: {preset.name} (v{preset.version})')

# New template structure following template/slots pattern
new_template_json = {
    "meta": {
        "id": "modern-landing-v2",
        "name": "Modern Landing",
        "version": "2.0.0",
        "category": "landing",
        "tier": "free",
        "description": "Modern landing page template with authentication and admin dashboard",
        "author": "Real Solutions",
        "tags": ["landing", "auth", "dashboard"]
    },
    "pages": {
        "/": {
            "template": "DashboardLayout",
            "slots": {
                "header": {
                    "type": "HeaderComposite",
                    "props": {
                        "title": "Welcome to Our Platform",
                        "subtitle": "Build amazing things together"
                    }
                },
                "main": {
                    "type": "Stack",
                    "props": {
                        "spacing": 4,
                        "sx": {"py": 4},
                        "children": [
                            {
                                "type": "Container",
                                "props": {
                                    "maxWidth": "lg",
                                    "children": [
                                        {
                                            "type": "Stack",
                                            "props": {
                                                "spacing": 3,
                                                "alignItems": "center",
                                                "textAlign": "center",
                                                "children": [
                                                    {
                                                        "type": "Heading",
                                                        "props": {
                                                            "level": 1,
                                                            "children": "Transform Your Business",
                                                            "sx": {"fontSize": {"xs": "2rem", "md": "3rem"}}
                                                        }
                                                    },
                                                    {
                                                        "type": "Text",
                                                        "props": {
                                                            "children": "Our platform helps you build, deploy, and scale your applications with ease. Join thousands of teams already using our solution.",
                                                            "variant": "h6",
                                                            "color": "text.secondary",
                                                            "sx": {"maxWidth": "800px"}
                                                        }
                                                    },
                                                    {
                                                        "type": "Stack",
                                                        "props": {
                                                            "direction": "row",
                                                            "spacing": 2,
                                                            "sx": {"mt": 2},
                                                            "children": [
                                                                {
                                                                    "type": "Button",
                                                                    "props": {
                                                                        "children": "Get Started",
                                                                        "variant": "contained",
                                                                        "color": "primary",
                                                                        "size": "large",
                                                                        "href": "/signup"
                                                                    }
                                                                },
                                                                {
                                                                    "type": "Button",
                                                                    "props": {
                                                                        "children": "Sign In",
                                                                        "variant": "outlined",
                                                                        "size": "large",
                                                                        "href": "/login"
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
                            },
                            {
                                "type": "Container",
                                "props": {
                                    "maxWidth": "lg",
                                    "sx": {"mt": 6},
                                    "children": [
                                        {
                                            "type": "Heading",
                                            "props": {
                                                "level": 2,
                                                "children": "Features",
                                                "sx": {"textAlign": "center", "mb": 4}
                                            }
                                        },
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "container": True,
                                                "spacing": 3,
                                                "children": [
                                                    {
                                                        "type": "Grid",
                                                        "props": {
                                                            "item": True,
                                                            "xs": 12,
                                                            "md": 4,
                                                            "children": [
                                                                {
                                                                    "type": "Card",
                                                                    "props": {
                                                                        "sx": {"p": 3, "height": "100%"},
                                                                        "children": [
                                                                            {
                                                                                "type": "Stack",
                                                                                "props": {
                                                                                    "spacing": 2,
                                                                                    "children": [
                                                                                        {
                                                                                            "type": "Heading",
                                                                                            "props": {
                                                                                                "level": 3,
                                                                                                "children": "🚀 Fast Deployment"
                                                                                            }
                                                                                        },
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "Deploy your applications in seconds with our streamlined workflow and automated processes."
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
                                                    },
                                                    {
                                                        "type": "Grid",
                                                        "props": {
                                                            "item": True,
                                                            "xs": 12,
                                                            "md": 4,
                                                            "children": [
                                                                {
                                                                    "type": "Card",
                                                                    "props": {
                                                                        "sx": {"p": 3, "height": "100%"},
                                                                        "children": [
                                                                            {
                                                                                "type": "Stack",
                                                                                "props": {
                                                                                    "spacing": 2,
                                                                                    "children": [
                                                                                        {
                                                                                            "type": "Heading",
                                                                                            "props": {
                                                                                                "level": 3,
                                                                                                "children": "🔒 Secure by Default"
                                                                                            }
                                                                                        },
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "Enterprise-grade security with end-to-end encryption and compliance certifications."
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
                                                    },
                                                    {
                                                        "type": "Grid",
                                                        "props": {
                                                            "item": True,
                                                            "xs": 12,
                                                            "md": 4,
                                                            "children": [
                                                                {
                                                                    "type": "Card",
                                                                    "props": {
                                                                        "sx": {"p": 3, "height": "100%"},
                                                                        "children": [
                                                                            {
                                                                                "type": "Stack",
                                                                                "props": {
                                                                                    "spacing": 2,
                                                                                    "children": [
                                                                                        {
                                                                                            "type": "Heading",
                                                                                            "props": {
                                                                                                "level": 3,
                                                                                                "children": "📊 Real-time Analytics"
                                                                                            }
                                                                                        },
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "Monitor your applications with comprehensive analytics and performance metrics."
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
        "/login": {
            "template": "CenterLayout",
            "slots": {
                "main": {
                    "type": "Container",
                    "props": {
                        "maxWidth": "sm",
                        "sx": {"py": 8},
                        "children": [
                            {
                                "type": "Card",
                                "props": {
                                    "sx": {"p": 4},
                                    "children": [
                                        {
                                            "type": "Stack",
                                            "props": {
                                                "spacing": 3,
                                                "children": [
                                                    {
                                                        "type": "Stack",
                                                        "props": {
                                                            "spacing": 1,
                                                            "alignItems": "center",
                                                            "children": [
                                                                {
                                                                    "type": "Heading",
                                                                    "props": {
                                                                        "level": 1,
                                                                        "children": "Sign In",
                                                                        "sx": {"fontSize": "2rem"}
                                                                    }
                                                                },
                                                                {
                                                                    "type": "Text",
                                                                    "props": {
                                                                        "children": "Welcome back! Please enter your credentials.",
                                                                        "color": "text.secondary"
                                                                    }
                                                                }
                                                            ]
                                                        }
                                                    },
                                                    {
                                                        "type": "LoginForm",
                                                        "props": {
                                                            "onSuccess": "/admin",
                                                            "showRememberMe": True,
                                                            "showForgotPassword": True
                                                        }
                                                    },
                                                    {
                                                        "type": "Divider",
                                                        "props": {
                                                            "sx": {"my": 2}
                                                        }
                                                    },
                                                    {
                                                        "type": "Stack",
                                                        "props": {
                                                            "direction": "row",
                                                            "justifyContent": "center",
                                                            "spacing": 1,
                                                            "children": [
                                                                {
                                                                    "type": "Text",
                                                                    "props": {
                                                                        "children": "Don't have an account?",
                                                                        "variant": "body2"
                                                                    }
                                                                },
                                                                {
                                                                    "type": "Link",
                                                                    "props": {
                                                                        "href": "/signup",
                                                                        "children": "Sign up"
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
                        ]
                    }
                }
            }
        },
        "/admin": {
            "template": "DashboardLayout",
            "slots": {
                "header": {
                    "type": "HeaderComposite",
                    "props": {
                        "title": "Dashboard",
                        "subtitle": "Welcome back! Here's what's happening."
                    }
                },
                "sidebar": {
                    "type": "Navigation",
                    "props": {
                        "items": [
                            {
                                "label": "Overview",
                                "href": "/admin",
                                "icon": "Dashboard"
                            },
                            {
                                "label": "Analytics",
                                "href": "/admin/analytics",
                                "icon": "BarChart"
                            },
                            {
                                "label": "Users",
                                "href": "/admin/users",
                                "icon": "People"
                            },
                            {
                                "label": "Settings",
                                "href": "/admin/settings",
                                "icon": "Settings"
                            },
                            {
                                "label": "Logout",
                                "href": "/logout",
                                "icon": "Logout"
                            }
                        ]
                    }
                },
                "main": {
                    "type": "Stack",
                    "props": {
                        "spacing": 3,
                        "children": [
                            {
                                "type": "Heading",
                                "props": {
                                    "level": 1,
                                    "children": "Dashboard Overview"
                                }
                            },
                            {
                                "type": "Grid",
                                "props": {
                                    "container": True,
                                    "spacing": 3,
                                    "children": [
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "item": True,
                                                "xs": 12,
                                                "md": 3,
                                                "children": [
                                                    {
                                                        "type": "Card",
                                                        "props": {
                                                            "sx": {"p": 3},
                                                            "children": [
                                                                {
                                                                    "type": "Stack",
                                                                    "props": {
                                                                        "spacing": 1,
                                                                        "children": [
                                                                            {
                                                                                "type": "Text",
                                                                                "props": {
                                                                                    "children": "Total Users",
                                                                                    "variant": "body2",
                                                                                    "color": "text.secondary"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Heading",
                                                                                "props": {
                                                                                    "level": 2,
                                                                                    "children": "2,543"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Chip",
                                                                                "props": {
                                                                                    "label": "+12.5%",
                                                                                    "color": "success",
                                                                                    "size": "small"
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
                                        },
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "item": True,
                                                "xs": 12,
                                                "md": 3,
                                                "children": [
                                                    {
                                                        "type": "Card",
                                                        "props": {
                                                            "sx": {"p": 3},
                                                            "children": [
                                                                {
                                                                    "type": "Stack",
                                                                    "props": {
                                                                        "spacing": 1,
                                                                        "children": [
                                                                            {
                                                                                "type": "Text",
                                                                                "props": {
                                                                                    "children": "Active Sessions",
                                                                                    "variant": "body2",
                                                                                    "color": "text.secondary"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Heading",
                                                                                "props": {
                                                                                    "level": 2,
                                                                                    "children": "342"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Chip",
                                                                                "props": {
                                                                                    "label": "+8.2%",
                                                                                    "color": "success",
                                                                                    "size": "small"
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
                                        },
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "item": True,
                                                "xs": 12,
                                                "md": 3,
                                                "children": [
                                                    {
                                                        "type": "Card",
                                                        "props": {
                                                            "sx": {"p": 3},
                                                            "children": [
                                                                {
                                                                    "type": "Stack",
                                                                    "props": {
                                                                        "spacing": 1,
                                                                        "children": [
                                                                            {
                                                                                "type": "Text",
                                                                                "props": {
                                                                                    "children": "Revenue",
                                                                                    "variant": "body2",
                                                                                    "color": "text.secondary"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Heading",
                                                                                "props": {
                                                                                    "level": 2,
                                                                                    "children": "$127.5K"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Chip",
                                                                                "props": {
                                                                                    "label": "+23.1%",
                                                                                    "color": "success",
                                                                                    "size": "small"
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
                                        },
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "item": True,
                                                "xs": 12,
                                                "md": 3,
                                                "children": [
                                                    {
                                                        "type": "Card",
                                                        "props": {
                                                            "sx": {"p": 3},
                                                            "children": [
                                                                {
                                                                    "type": "Stack",
                                                                    "props": {
                                                                        "spacing": 1,
                                                                        "children": [
                                                                            {
                                                                                "type": "Text",
                                                                                "props": {
                                                                                    "children": "Conversion Rate",
                                                                                    "variant": "body2",
                                                                                    "color": "text.secondary"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Heading",
                                                                                "props": {
                                                                                    "level": 2,
                                                                                    "children": "3.2%"
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Chip",
                                                                                "props": {
                                                                                    "label": "+1.8%",
                                                                                    "color": "success",
                                                                                    "size": "small"
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
                                    ]
                                }
                            },
                            {
                                "type": "Grid",
                                "props": {
                                    "container": True,
                                    "spacing": 3,
                                    "children": [
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "item": True,
                                                "xs": 12,
                                                "md": 8,
                                                "children": [
                                                    {
                                                        "type": "Card",
                                                        "props": {
                                                            "sx": {"p": 3},
                                                            "children": [
                                                                {
                                                                    "type": "Heading",
                                                                    "props": {
                                                                        "level": 3,
                                                                        "children": "Recent Activity",
                                                                        "sx": {"mb": 2}
                                                                    }
                                                                },
                                                                {
                                                                    "type": "Stack",
                                                                    "props": {
                                                                        "spacing": 2,
                                                                        "children": [
                                                                            {
                                                                                "type": "Stack",
                                                                                "props": {
                                                                                    "direction": "row",
                                                                                    "justifyContent": "space-between",
                                                                                    "alignItems": "center",
                                                                                    "children": [
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "New user registration"
                                                                                            }
                                                                                        },
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "2 minutes ago",
                                                                                                "variant": "body2",
                                                                                                "color": "text.secondary"
                                                                                            }
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Divider",
                                                                                "props": {}
                                                                            },
                                                                            {
                                                                                "type": "Stack",
                                                                                "props": {
                                                                                    "direction": "row",
                                                                                    "justifyContent": "space-between",
                                                                                    "alignItems": "center",
                                                                                    "children": [
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "Payment received"
                                                                                            }
                                                                                        },
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "15 minutes ago",
                                                                                                "variant": "body2",
                                                                                                "color": "text.secondary"
                                                                                            }
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Divider",
                                                                                "props": {}
                                                                            },
                                                                            {
                                                                                "type": "Stack",
                                                                                "props": {
                                                                                    "direction": "row",
                                                                                    "justifyContent": "space-between",
                                                                                    "alignItems": "center",
                                                                                    "children": [
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "Support ticket created"
                                                                                            }
                                                                                        },
                                                                                        {
                                                                                            "type": "Text",
                                                                                            "props": {
                                                                                                "children": "1 hour ago",
                                                                                                "variant": "body2",
                                                                                                "color": "text.secondary"
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
                                                ]
                                            }
                                        },
                                        {
                                            "type": "Grid",
                                            "props": {
                                                "item": True,
                                                "xs": 12,
                                                "md": 4,
                                                "children": [
                                                    {
                                                        "type": "Card",
                                                        "props": {
                                                            "sx": {"p": 3},
                                                            "children": [
                                                                {
                                                                    "type": "Heading",
                                                                    "props": {
                                                                        "level": 3,
                                                                        "children": "Quick Actions",
                                                                        "sx": {"mb": 2}
                                                                    }
                                                                },
                                                                {
                                                                    "type": "Stack",
                                                                    "props": {
                                                                        "spacing": 2,
                                                                        "children": [
                                                                            {
                                                                                "type": "Button",
                                                                                "props": {
                                                                                    "children": "Create User",
                                                                                    "variant": "outlined",
                                                                                    "fullWidth": True
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Button",
                                                                                "props": {
                                                                                    "children": "View Reports",
                                                                                    "variant": "outlined",
                                                                                    "fullWidth": True
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "Button",
                                                                                "props": {
                                                                                    "children": "Export Data",
                                                                                    "variant": "outlined",
                                                                                    "fullWidth": True
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
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
}

# Update the preset
preset.template_json = new_template_json
preset.version = '2.0.0'
preset.save()

print(f'\n✅ Updated Modern Landing preset to v2.0.0')
print(f'\nNew pages:')
for page_path in new_template_json['pages'].keys():
    page = new_template_json['pages'][page_path]
    template = page.get('template', 'Unknown')
    print(f'  {page_path}: {template}')

print(f'\n📝 Page details:')
print(f'  / - Landing page with hero, features, and CTAs')
print(f'  /login - Authentication page with LoginForm component')
print(f'  /admin - Dashboard with stats cards, activity feed, and quick actions')

print(f'\n✅ Template preset updated successfully!')
