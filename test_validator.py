#!/usr/bin/env python3
"""
Test the updated validator to ensure it only accepts template/slots format.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.validators import validate_template_json
from django.core.exceptions import ValidationError

print("=" * 80)
print("TESTING TEMPLATE VALIDATOR - NEW FORMAT ONLY")
print("=" * 80)

# Test 1: Valid new format
print("\n✅ Test 1: Valid template/slots format")
valid_new = {
    "meta": {
        "id": "test-template",
        "name": "Test Template",
        "version": "1.0.0",
        "category": "landing",
        "tier": "free"
    },
    "pages": {
        "/": {
            "template": "DashboardLayout",
            "slots": {
                "main": {
                    "type": "Container",
                    "props": {"children": "Hello"}
                }
            }
        }
    }
}

try:
    validate_template_json(valid_new)
    print("   ✓ Passed - New format accepted")
except ValidationError as e:
    print(f"   ✗ Failed - {e}")

# Test 2: Invalid old format (should FAIL)
print("\n❌ Test 2: Old sections format (should be REJECTED)")
invalid_old = {
    "meta": {
        "id": "old-template",
        "name": "Old Template",
        "version": "1.0.0",
        "category": "landing",
        "tier": "free"
    },
    "pages": {
        "home": {
            "id": "home",
            "title": "Home",
            "layout": {"type": "default-layout"},
            "sections": [
                {"id": "hero", "type": "hero-simple"}
            ]
        }
    }
}

try:
    validate_template_json(invalid_old)
    print("   ✗ Failed - Old format was accepted (should be rejected!)")
except ValidationError as e:
    print(f"   ✓ Passed - Old format correctly rejected")
    print(f"      Errors: {e}")

# Test 3: Missing template field
print("\n❌ Test 3: Missing 'template' field (should be REJECTED)")
missing_template = {
    "meta": {
        "id": "test",
        "name": "Test",
        "version": "1.0.0",
        "category": "landing",
        "tier": "free"
    },
    "pages": {
        "/": {
            "slots": {"main": {}}
        }
    }
}

try:
    validate_template_json(missing_template)
    print("   ✗ Failed - Missing template was accepted")
except ValidationError as e:
    print(f"   ✓ Passed - Missing template correctly rejected")

# Test 4: Missing slots field
print("\n❌ Test 4: Missing 'slots' field (should be REJECTED)")
missing_slots = {
    "meta": {
        "id": "test",
        "name": "Test",
        "version": "1.0.0",
        "category": "landing",
        "tier": "free"
    },
    "pages": {
        "/": {
            "template": "DashboardLayout"
        }
    }
}

try:
    validate_template_json(missing_slots)
    print("   ✗ Failed - Missing slots was accepted")
except ValidationError as e:
    print(f"   ✓ Passed - Missing slots correctly rejected")

# Test 5: Empty slots
print("\n❌ Test 5: Empty slots object (should be REJECTED)")
empty_slots = {
    "meta": {
        "id": "test",
        "name": "Test",
        "version": "1.0.0",
        "category": "landing",
        "tier": "free"
    },
    "pages": {
        "/": {
            "template": "DashboardLayout",
            "slots": {}
        }
    }
}

try:
    validate_template_json(empty_slots)
    print("   ✗ Failed - Empty slots was accepted")
except ValidationError as e:
    print(f"   ✓ Passed - Empty slots correctly rejected")

# Test 6: Template must be string
print("\n❌ Test 6: Template as object instead of string (should be REJECTED)")
template_object = {
    "meta": {
        "id": "test",
        "name": "Test",
        "version": "1.0.0",
        "category": "landing",
        "tier": "free"
    },
    "pages": {
        "/": {
            "template": {"type": "DashboardLayout"},
            "slots": {"main": {}}
        }
    }
}

try:
    validate_template_json(template_object)
    print("   ✗ Failed - Template object was accepted")
except ValidationError as e:
    print(f"   ✓ Passed - Template object correctly rejected")

print("\n" + "=" * 80)
print("VALIDATION TESTS COMPLETE")
print("=" * 80)
print("\n✅ Validator now enforces ONLY the new template/slots format!")
print("❌ Old sections-based format is no longer supported.")
