#!/usr/bin/env python
"""Create TenantFeatureFlag table directly using Django schema editor."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import TenantFeatureFlag
from django.db import connections

connection = connections['default']
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(TenantFeatureFlag)
    
print('✓ tenant_feature_flags table created successfully')
