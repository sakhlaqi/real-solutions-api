"""
Management command to create API clients.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.authentication.models import APIClient
from apps.tenants.models import Tenant
import json


class Command(BaseCommand):
    help = 'Create a new API client for machine-to-machine authentication'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Display name for the API client'
        )
        
        parser.add_argument(
            '--tenant',
            type=str,
            required=True,
            help='Tenant slug or ID'
        )
        
        parser.add_argument(
            '--description',
            type=str,
            default='',
            help='Description of the API client purpose'
        )
        
        parser.add_argument(
            '--roles',
            type=str,
            default='',
            help='Comma-separated list of roles (e.g., "read,write,admin")'
        )
        
        parser.add_argument(
            '--scopes',
            type=str,
            default='',
            help='Comma-separated list of scopes (e.g., "read:projects,write:projects")'
        )
        
        parser.add_argument(
            '--allowed-ips',
            type=str,
            default='',
            help='Comma-separated list of allowed IP addresses'
        )
        
        parser.add_argument(
            '--rate-limit',
            type=int,
            help='Custom rate limit (requests per hour)'
        )
        
        parser.add_argument(
            '--output-json',
            action='store_true',
            help='Output credentials as JSON'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        """
        Create the API client.
        """
        name = options['name']
        tenant_identifier = options['tenant']
        description = options['description']
        roles = [r.strip() for r in options['roles'].split(',') if r.strip()]
        scopes = [s.strip() for s in options['scopes'].split(',') if s.strip()]
        allowed_ips = [ip.strip() for ip in options['allowed_ips'].split(',') if ip.strip()]
        rate_limit = options.get('rate_limit')
        output_json = options.get('output_json', False)
        
        # Resolve tenant
        tenant = None
        
        # First try by slug
        try:
            tenant = Tenant.objects.get(slug=tenant_identifier)
        except Tenant.DoesNotExist:
            # If not found by slug, try by ID (if it looks like a UUID)
            try:
                import uuid
                uuid.UUID(tenant_identifier)  # Validate it's a UUID format
                tenant = Tenant.objects.get(id=tenant_identifier)
            except (ValueError, Tenant.DoesNotExist):
                raise CommandError(
                    f"Tenant '{tenant_identifier}' not found. "
                    f"Please provide a valid tenant slug or UUID."
                )
        
        if not tenant.is_active:
            raise CommandError(f"Tenant '{tenant.slug}' is not active")
        
        # Generate credentials
        client_id = APIClient.generate_client_id()
        client_secret = APIClient.generate_client_secret()
        
        # Create API client
        api_client = APIClient.objects.create(
            client_id=client_id,
            name=name,
            description=description,
            tenant=tenant,
            roles=roles,
            scopes=scopes,
            allowed_ips=allowed_ips,
            rate_limit=rate_limit,
        )
        
        # Set the secret
        api_client.set_client_secret(client_secret)
        api_client.save(update_fields=['client_secret_hash'])
        
        # Output credentials
        if output_json:
            output = {
                'id': str(api_client.id),
                'client_id': client_id,
                'client_secret': client_secret,
                'name': name,
                'tenant': {
                    'id': str(tenant.id),
                    'slug': tenant.slug,
                    'name': tenant.name,
                },
                'roles': roles,
                'scopes': scopes,
                'allowed_ips': allowed_ips,
                'rate_limit': rate_limit,
                'created_at': api_client.created_at.isoformat(),
            }
            self.stdout.write(json.dumps(output, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
            self.stdout.write(self.style.SUCCESS('API Client Created Successfully'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write(f'\nName:        {name}')
            self.stdout.write(f'Tenant:      {tenant.name} ({tenant.slug})')
            self.stdout.write(f'ID:          {api_client.id}')
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('CLIENT CREDENTIALS (save these securely):'))
            self.stdout.write(self.style.WARNING('-' * 70))
            self.stdout.write(self.style.WARNING(f'Client ID:     {client_id}'))
            self.stdout.write(self.style.WARNING(f'Client Secret: {client_secret}'))
            self.stdout.write(self.style.WARNING('-' * 70))
            self.stdout.write(self.style.WARNING('\n⚠️  IMPORTANT: Save these credentials now!'))
            self.stdout.write(self.style.WARNING('The client secret cannot be retrieved later.\n'))
            
            if roles:
                self.stdout.write(f'Roles:       {", ".join(roles)}')
            if scopes:
                self.stdout.write(f'Scopes:      {", ".join(scopes)}')
            if allowed_ips:
                self.stdout.write(f'Allowed IPs: {", ".join(allowed_ips)}')
            if rate_limit:
                self.stdout.write(f'Rate Limit:  {rate_limit} requests/hour')
            
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write('\nToken endpoint: POST /api/v1/auth/api-client/token/')
            self.stdout.write('\nExample request:')
            self.stdout.write('  curl -X POST http://localhost:8000/api/v1/auth/api-client/token/ \\')
            self.stdout.write('    -H "Content-Type: application/json" \\')
            self.stdout.write('    -d \'{"client_id": "' + client_id + '", "client_secret": "' + client_secret + '"}\'')
            self.stdout.write('')
