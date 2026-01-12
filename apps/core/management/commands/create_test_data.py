"""
Management command to create sample tenant data for testing.

Usage:
    python manage.py create_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.core.models import Project, Task, Document
from apps.authentication.utils import generate_tenant_token
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample tenant data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating test data...\n')
        
        # Create tenants
        tenant1 = Tenant.objects.create(
            name='Acme Corporation',
            slug='acme',
            is_active=True,
            metadata={'industry': 'Technology', 'size': 'Large'}
        )
        self.stdout.write(f'✓ Created tenant: {tenant1.name} (ID: {tenant1.id})')
        
        tenant2 = Tenant.objects.create(
            name='Beta Solutions',
            slug='beta',
            is_active=True,
            metadata={'industry': 'Finance', 'size': 'Medium'}
        )
        self.stdout.write(f'✓ Created tenant: {tenant2.name} (ID: {tenant2.id})')
        
        # Create users
        user1 = User.objects.create_user(
            username='acme_user',
            email='user@acme.com',
            password='testpass123'
        )
        self.stdout.write(f'✓ Created user: {user1.username}')
        
        user2 = User.objects.create_user(
            username='beta_user',
            email='user@beta.com',
            password='testpass123'
        )
        self.stdout.write(f'✓ Created user: {user2.username}')
        
        # Create projects for Acme
        project1 = Project.objects.create(
            tenant=tenant1,
            name='Website Redesign',
            description='Redesign company website with modern UI',
            status='active'
        )
        
        project2 = Project.objects.create(
            tenant=tenant1,
            name='Mobile App Development',
            description='Build iOS and Android mobile applications',
            status='active'
        )
        self.stdout.write(f'✓ Created {2} projects for {tenant1.name}')
        
        # Create projects for Beta
        project3 = Project.objects.create(
            tenant=tenant2,
            name='API Integration',
            description='Integrate third-party payment APIs',
            status='active'
        )
        self.stdout.write(f'✓ Created {1} project for {tenant2.name}')
        
        # Create tasks for Acme projects
        Task.objects.create(
            tenant=tenant1,
            project=project1,
            title='Design wireframes',
            description='Create wireframes for all pages',
            status='done',
            priority='high'
        )
        
        Task.objects.create(
            tenant=tenant1,
            project=project1,
            title='Implement homepage',
            description='Code the new homepage design',
            status='in_progress',
            priority='high'
        )
        
        Task.objects.create(
            tenant=tenant1,
            project=project2,
            title='Setup development environment',
            description='Configure React Native development',
            status='done',
            priority='critical'
        )
        self.stdout.write(f'✓ Created {3} tasks for {tenant1.name}')
        
        # Create tasks for Beta projects
        Task.objects.create(
            tenant=tenant2,
            project=project3,
            title='Research payment providers',
            description='Compare Stripe, PayPal, and Square',
            status='todo',
            priority='medium'
        )
        self.stdout.write(f'✓ Created {1} task for {tenant2.name}')
        
        # Create documents
        Document.objects.create(
            tenant=tenant1,
            project=project1,
            name='Design Specifications.pdf',
            file_path='/uploads/acme/design-specs.pdf',
            file_size=2048576,
            content_type='application/pdf',
            metadata={'author': 'Design Team', 'version': '1.0'}
        )
        
        Document.objects.create(
            tenant=tenant2,
            project=project3,
            name='API Documentation.md',
            file_path='/uploads/beta/api-docs.md',
            file_size=51200,
            content_type='text/markdown',
            metadata={'author': 'Dev Team', 'version': '1.0'}
        )
        self.stdout.write(f'✓ Created documents')
        
        # Generate JWT tokens for testing
        self.stdout.write('\n' + '='*60)
        self.stdout.write('JWT TOKENS FOR TESTING')
        self.stdout.write('='*60 + '\n')
        
        tokens1 = generate_tenant_token(user1, tenant1)
        self.stdout.write(f'User: {user1.username} @ {tenant1.slug}')
        self.stdout.write(f'Access Token:\n{tokens1["access"]}\n')
        
        tokens2 = generate_tenant_token(user2, tenant2)
        self.stdout.write(f'User: {user2.username} @ {tenant2.slug}')
        self.stdout.write(f'Access Token:\n{tokens2["access"]}\n')
        
        # Save to file for easy access
        test_data = {
            'tenants': [
                {
                    'id': str(tenant1.id),
                    'name': tenant1.name,
                    'slug': tenant1.slug,
                    'user': user1.username,
                    'access_token': tokens1['access'],
                    'refresh_token': tokens1['refresh'],
                },
                {
                    'id': str(tenant2.id),
                    'name': tenant2.name,
                    'slug': tenant2.slug,
                    'user': user2.username,
                    'access_token': tokens2['access'],
                    'refresh_token': tokens2['refresh'],
                }
            ]
        }
        
        with open('test_tokens.json', 'w') as f:
            json.dump(test_data, f, indent=2)
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('✓ Test data created successfully!'))
        self.stdout.write(self.style.SUCCESS('✓ Tokens saved to test_tokens.json'))
