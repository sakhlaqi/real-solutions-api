# Template Validation - New Format Only

## Change Summary

The template validator has been updated to **enforce only** the new template/slots format. The old sections-based format is **no longer supported**.

## Required Format

All template pages must follow this structure:

```json
{
  "meta": {
    "id": "template-id",
    "name": "Template Name",
    "version": "1.0.0",
    "category": "landing",
    "tier": "free"
  },
  "pages": {
    "/path": {
      "template": "LayoutName",      // Required: String
      "slots": {                      // Required: Non-empty object
        "slotName": {
          "type": "ComponentName",
          "props": { ... }
        }
      }
    }
  }
}
```

## Validation Rules

### ✅ Required Fields

Each page **must** have:
1. **`template`** - String name of the layout component
   - Example: `"DashboardLayout"`, `"CenterLayout"`, `"TwoColumnLayout"`
   
2. **`slots`** - Object with slot configurations
   - Must be a non-empty object
   - Each slot contains component configuration

### ❌ Rejected Patterns

The following are **no longer valid**:

#### Old sections format:
```json
{
  "id": "home",
  "title": "Home",
  "layout": { "type": "default-layout" },
  "sections": [...]
}
```
**Error:** `template_json.pages.home.template is required`

#### Missing template:
```json
{
  "slots": { "main": {...} }
}
```
**Error:** `template_json.pages./.template is required`

#### Missing slots:
```json
{
  "template": "DashboardLayout"
}
```
**Error:** `template_json.pages./.slots is required`

#### Empty slots:
```json
{
  "template": "DashboardLayout",
  "slots": {}
}
```
**Error:** `template_json.pages./.slots cannot be empty`

#### Template as object:
```json
{
  "template": { "type": "DashboardLayout" },
  "slots": { "main": {...} }
}
```
**Error:** `template_json.pages./.template must be a string`

## Migration Guide

If you have templates using the old format, migrate them as follows:

### Before (Old Format):
```json
{
  "id": "home",
  "title": "Home",
  "layout": {
    "type": "default-layout",
    "version": "1.0.0"
  },
  "sections": [
    {
      "id": "hero",
      "type": "hero-simple",
      "props": {
        "heading": "Welcome"
      }
    }
  ]
}
```

### After (New Format):
```json
{
  "template": "DashboardLayout",
  "slots": {
    "main": {
      "type": "Stack",
      "props": {
        "spacing": 3,
        "children": [
          {
            "type": "Heading",
            "props": {
              "level": 1,
              "children": "Welcome"
            }
          }
        ]
      }
    }
  }
}
```

## Benefits of New Format

1. **Clarity:** Direct mapping between layout templates and page structure
2. **Type Safety:** String template names are easier to validate
3. **Consistency:** All pages follow the same pattern
4. **Flexibility:** Slots can contain any component composition
5. **Maintainability:** No legacy code paths to support

## Testing

Run the validation test suite:
```bash
cd api
python3 test_validator.py
```

All 6 tests should pass:
- ✅ Valid template/slots format accepted
- ✅ Old sections format rejected
- ✅ Missing template rejected
- ✅ Missing slots rejected
- ✅ Empty slots rejected
- ✅ Template as object rejected

## Existing Templates

The Modern Landing v2.0.0 preset has been updated and validates successfully:
- `/` - Landing page
- `/login` - Authentication page
- `/admin` - Dashboard page

All use the new template/slots format.

## Code Changes

**Modified:** `api/apps/tenants/validators.py`
- Removed `_validate_section_reference()` function
- Simplified `_validate_page_definition()` to only check template/slots
- Removed all legacy format support

**Line count:** Reduced from ~45 lines to ~25 lines in validation logic

## Impact

- **Breaking Change:** Old templates will fail validation
- **Action Required:** Migrate any existing templates to new format
- **Timeline:** Immediate - all new templates must use new format
