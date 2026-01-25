"""
Management command to configure tenant routes.
Usage: python manage.py configure_routes <tenant_slug> [--preset=<preset>]
"""

from django.core.management.base import BaseCommand, CommandError
from apps.tenants.models import Tenant


# Default routes preset
DEFAULT_ROUTES = [
    {
        'path': '/',
        'pagePath': '/',
        'title': 'Home',
        'protected': False,
        'layout': 'main',
        'order': 0
    },
    {
        'path': '/login',
        'pagePath': '/login',
        'title': 'Login',
        'protected': False,
        'layout': 'none',
        'order': 1
    },
    {
        'path': '/admin',
        'pagePath': '/dashboard',
        'title': 'Dashboard',
        'protected': True,
        'layout': 'admin',
        'order': 2
    }
]

# Construction company preset
CONSTRUCTION_ROUTES = [
    {
        'path': '/',
        'pagePath': '/',
        'title': 'Home',
        'protected': False,
        'layout': 'main'
    },
    {
        'path': '/login',
        'pagePath': '/login',
        'title': 'Login',
        'protected': False,
        'layout': 'none'
    },
    {
        'path': '/admin',
        'pagePath': '/dashboard',
        'title': 'Dashboard',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/projects',
        'pagePath': '/projects',
        'title': 'Projects',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/projects/:id',
        'pagePath': '/projects/:id',
        'title': 'Project Details',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/equipment',
        'pagePath': '/equipment',
        'title': 'Equipment',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/employees',
        'pagePath': '/employees',
        'title': 'Employees',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/employees/:id',
        'pagePath': '/employees/:id',
        'title': 'Employee Details',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/settings',
        'pagePath': '/settings',
        'title': 'Settings',
        'protected': True,
        'layout': 'admin'
    }
]

# HR firm preset
HR_ROUTES = [
    {
        'path': '/',
        'pagePath': '/',
        'title': 'Home',
        'protected': False,
        'layout': 'main'
    },
    {
        'path': '/login',
        'pagePath': '/login',
        'title': 'Login',
        'protected': False,
        'layout': 'none'
    },
    {
        'path': '/admin',
        'pagePath': '/dashboard',
        'title': 'Dashboard',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/employees',
        'pagePath': '/employees',
        'title': 'Employees',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/employees/:id',
        'pagePath': '/employees/:id',
        'title': 'Employee Profile',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/payroll',
        'pagePath': '/payroll',
        'title': 'Payroll',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/benefits',
        'pagePath': '/benefits',
        'title': 'Benefits',
        'protected': True,
        'layout': 'admin'
    },
    {
        'path': '/admin/settings',
        'pagePath': '/settings',
        'title': 'Settings',
        'protected': True,
        'layout': 'admin'
    }
]

PRESETS = {
    'default': DEFAULT_ROUTES,
    'construction': CONSTRUCTION_ROUTES,
    'hr': HR_ROUTES,
}


class Command(BaseCommand):
    help = 'Configure routes for a tenant'

    def add_arguments(self, parser):
        parser.add_argument(
            'tenant_slug',
            type=str,
            help='Slug of the tenant to configure'
        )
        parser.add_argument(
            '--preset',
            type=str,
            default='default',
            choices=['default', 'construction', 'hr', 'custom'],
            help='Route preset to use'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List current routes for the tenant'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all routes for the tenant'
        )

    def handle(self, *args, **options):
        tenant_slug = options['tenant_slug']
        preset = options['preset']
        list_routes = options['list']
        clear_routes = options['clear']

        # Get tenant
        try:
            tenant = Tenant.objects.get(slug=tenant_slug)
        except Tenant.DoesNotExist:
            raise CommandError(f'Tenant "{tenant_slug}" does not exist')

        # List routes
        if list_routes:
            current_routes = tenant.metadata.get('routes', [])
            if not current_routes:
                self.stdout.write(
                    self.style.WARNING(f'No routes configured for {tenant.name}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'\nRoutes for {tenant.name}:\n')
                )
                for i, route in enumerate(current_routes, 1):
                    protected = '🔒' if route.get('protected') else '🌐'
                    self.stdout.write(
                        f"  {i}. {protected} {route.get('path')} - {route.get('title')} [{route.get('layout')}]"
                    )
            return

        # Clear routes
        if clear_routes:
            tenant.metadata['routes'] = []
            tenant.save()
            self.stdout.write(
                self.style.SUCCESS(f'Cleared all routes for {tenant.name}')
            )
            return

        # Set routes from preset
        if preset != 'custom':
            routes = PRESETS[preset]
            
            # Update tenant metadata
            metadata = tenant.metadata.copy()
            metadata['routes'] = routes
            tenant.metadata = metadata
            tenant.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully configured {preset} routes for {tenant.name}\n'
                )
            )
            self.stdout.write(f'  Total routes: {len(routes)}')
            
            # Show routes
            self.stdout.write('\n  Routes configured:')
            for route in routes:
                protected = '🔒' if route.get('protected') else '🌐'
                self.stdout.write(
                    f"    {protected} {route.get('path')} - {route.get('title')}"
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Routes are now available at: /api/v1/tenants/{tenant_slug}/config/\n'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Custom preset selected. Please update routes manually via Django admin or API.'
                )
            )
