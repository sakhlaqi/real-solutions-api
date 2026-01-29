"""
Create a test user for development and testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a test user for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='test@acme.com',
            help='Email address for the test user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='password123',
            help='Password for the test user'
        )
        parser.add_argument(
            '--tenant',
            type=str,
            default='acme',
            help='Tenant slug'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        tenant_slug = options['tenant']
        
        try:
            # Get tenant
            tenant = Tenant.objects.get(slug=tenant_slug)
            self.stdout.write(f'Found tenant: {tenant.name} ({tenant.slug})')
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tenant "{tenant_slug}" does not exist'))
            return
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            self.stdout.write(self.style.WARNING(f'User "{email}" already exists'))
            # Update password
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated password for user "{email}"'))
        else:
            # Create user
            user = User.objects.create_user(
                username=email.split('@')[0],
                email=email,
                password=password,
                first_name='Test',
                last_name='User',
            )
            self.stdout.write(self.style.SUCCESS(f'Created user "{email}"'))
        
        # Link user to tenant (if your model supports this)
        # You may need to adjust this based on your TenantMembership model
        self.stdout.write(self.style.SUCCESS(
            f'\nTest user created successfully!\n'
            f'Email: {email}\n'
            f'Password: {password}\n'
            f'Tenant: {tenant_slug}\n'
        ))
