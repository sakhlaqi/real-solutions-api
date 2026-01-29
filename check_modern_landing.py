#!/usr/bin/env python3
"""
Check and update the Modern Landing template preset.
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Template

# Find the Modern Landing preset
preset = Template.objects.filter(is_preset=True, name__icontains='Modern Landing').first()

if preset:
    print('=' * 80)
    print('CURRENT MODERN LANDING PRESET')
    print('=' * 80)
    print(f'Name: {preset.name}')
    print(f'Category: {preset.category}')
    print(f'Version: {preset.version}')
    
    print(f'\nCurrent template_json keys: {list(preset.template_json.keys())}')
    
    if 'pages' in preset.template_json:
        pages = preset.template_json['pages']
        print(f'\nPages: {list(pages.keys())}')
        
        # Show structure of first page
        if pages:
            first_page_key = list(pages.keys())[0]
            first_page = pages[first_page_key]
            print(f'\nExample page ({first_page_key}) structure:')
            print(json.dumps(first_page, indent=2)[:500])
    
    print('\n' + '=' * 80)
    print('FULL template_json:')
    print('=' * 80)
    print(json.dumps(preset.template_json, indent=2))
else:
    print('No Modern Landing preset found!')
    print('\nAll presets:')
    for p in Template.objects.filter(is_preset=True):
        print(f'  - {p.name} ({p.category})')
