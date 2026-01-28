# Template System - ACME Example

This document demonstrates the Template system working end-to-end with the ACME tenant.

## Overview

The Template system works exactly like the Theme system:
- **Presets**: Immutable, reusable templates provided by Real Solutions
- **Custom Templates**: Tenant-specific templates that inherit from presets
- **Overrides**: Customizations that merge with preset defaults at runtime
- **Resolution**: Automatic merging of preset + overrides to create final template

## What Was Created

### 1. Template Presets (2 total)

#### Modern Landing (Free Tier)
- **ID**: `9398f604-42cd-4710-bfc7-a7c3d398ffb1`
- **Category**: landing
- **Tier**: free
- **Sections**: Hero, Features Grid, CTA
- **Use Case**: Product launches, lead generation

#### Professional Marketing (Premium Tier)
- **ID**: `d04961b0-461a-4939-80d8-f2d021d90b6d`
- **Category**: marketing
- **Tier**: premium
- **Sections**: Hero with Image, Stats Grid, Testimonials
- **Use Case**: Professional marketing pages

### 2. ACME Custom Template

**Name**: ACME Modern Landing (Custom)
**ID**: `550e3d51-4968-4578-81a1-c829df2d20e9`
**Base Preset**: Modern Landing
**Tenant**: ACME Corporation

#### Customizations Applied

1. **Hero Section**
   - Changed heading: "Transform Your Business" → "Welcome to ACME Corporation"
   - Changed subheading: "Discover cutting-edge solutions..." → "Industry-leading solutions since 1985"
   - Changed CTA: "Get Started" → "Explore Our Products"
   - Changed alignment: center → left
   - Applied ACME brand gradient colors

2. **Features Section**
   - Changed title: "Why Choose Us" → "ACME Advantages"
   - Customized all 3 feature items with ACME-specific messaging:
     - "Innovation First"
     - "35+ Years Experience"
     - "Expert Team"

3. **CTA Section**
   - Changed heading: "Ready to Get Started?" → "Partner with ACME Today"
   - Changed primary button: "Sign Up Now" → "Request a Demo"
   - Changed secondary button: "Learn More" → "Contact Sales"

## How It Works

### Template Resolution

```python
# Get ACME's active template
acme = Tenant.objects.get(slug='acme')
template = acme.template

# This returns the fully merged template
resolved = template.get_resolved_template_json()
```

**Resolution Process**:
1. Start with base preset structure (`Modern Landing`)
2. Deep merge with ACME's overrides
3. Return final template with ACME branding

### Database Structure

```
Template Presets (is_preset=True, tenant=NULL)
├── Modern Landing
└── Professional Marketing

Custom Templates (is_preset=False, tenant=ACME)
└── ACME Modern Landing (Custom)
    └── base_preset → Modern Landing
```

## Scripts Created

### 1. `seed_template_presets.py`
Management command to seed template presets:
```bash
python manage.py seed_template_presets
```

### 2. `configure_acme_template.py`
Script to configure ACME with template + overrides:
```bash
python configure_acme_template.py
```

### 3. `verify_acme_template.py`
Verification script showing template resolution:
```bash
python verify_acme_template.py
```

### 4. `test_template_api.py`
Query examples and API endpoint summary:
```bash
python test_template_api.py
```

## API Endpoints

### Public (No Authentication)

```
GET /api/tenants/templates/presets/
GET /api/tenants/templates/by_category/?category=landing
GET /api/tenants/templates/by_tier/?tier=free
```

### Authenticated (Requires Tenant Token)

```
GET    /api/tenants/templates/              # List all (presets + custom)
GET    /api/tenants/templates/{id}/         # Get specific template
POST   /api/tenants/templates/              # Create custom template
PUT    /api/tenants/templates/{id}/         # Update custom template
DELETE /api/tenants/templates/{id}/         # Delete custom template
POST   /api/tenants/templates/{id}/clone/   # Clone preset to custom
```

## Key Features Demonstrated

✅ **Template Presets**: Immutable, reusable base templates
✅ **Inheritance**: Custom templates inherit from presets
✅ **Overrides**: Deep merge of customizations with preset
✅ **Resolution**: Runtime merging of preset + overrides
✅ **Multi-Category**: landing, marketing templates
✅ **Multi-Tier**: free, premium classification
✅ **Tenant Assignment**: ACME using custom template
✅ **API Endpoints**: Full CRUD + filtering
✅ **Validation**: JSON schema validation on save

## Template JSON Structure

```json
{
  "meta": {
    "id": "uuid",
    "name": "Template Name",
    "version": "1.0.0",
    "category": "landing",
    "tier": "free"
  },
  "pages": {
    "home": {
      "id": "home",
      "title": "Home",
      "sections": [
        {
          "id": "hero",
          "type": "hero-simple",
          "version": "1.0.0",
          "props": { /* section properties */ }
        }
      ]
    }
  }
}
```

## Next Steps (Phase 2)

When ready to add entitlements:
1. Link subscription plans to tier field
2. Add entitlement checks in template selection
3. Restrict premium templates based on subscription
4. Add template marketplace/gallery UI

**Important**: Entitlements only affect selection, not rendering. Templates remain decoupled from billing logic.

## Verification Checklist

✅ Preset templates seeded in database
✅ ACME tenant using custom template
✅ Custom template inherits from preset
✅ Overrides successfully applied
✅ Template resolution working correctly
✅ All 3 sections customized (hero, features, cta)
✅ Database constraints enforced
✅ API endpoints functional

---

**Generated**: 2026-01-27
**Phase**: Phase 1 Complete
**Status**: ✅ Ready for Production
