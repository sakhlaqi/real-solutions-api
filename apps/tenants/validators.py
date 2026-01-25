"""
Theme JSON Schema Validator

Validates theme JSON data against the canonical schema from UI library.
This ensures themes stored in the database conform to the expected structure.
"""

from django.core.exceptions import ValidationError
from typing import Dict, Any, List


def validate_theme_json(theme_json: Dict[str, Any]) -> None:
    """
    Validate theme JSON structure.
    
    Validates against the schema defined in the UI library.
    Raises ValidationError if validation fails.
    
    Args:
        theme_json: Theme data to validate
        
    Raises:
        ValidationError: If theme_json is invalid
    """
    errors = []
    
    # Check top-level structure
    if not isinstance(theme_json, dict):
        raise ValidationError("theme_json must be a dictionary")
    
    # Validate meta
    errors.extend(_validate_meta(theme_json.get('meta')))
    
    # Validate tokens
    errors.extend(_validate_tokens(theme_json.get('tokens')))
    
    # Validate modes (optional)
    if 'modes' in theme_json:
        errors.extend(_validate_modes(theme_json.get('modes')))
    
    if errors:
        raise ValidationError(errors)


def _validate_meta(meta: Any) -> List[str]:
    """Validate theme meta."""
    errors = []
    
    if not isinstance(meta, dict):
        return ["theme_json.meta must be a dictionary"]
    
    # Required fields
    required = ['id', 'name', 'version', 'category']
    for field in required:
        if field not in meta:
            errors.append(f"theme_json.meta.{field} is required")
    
    # Validate types
    if 'id' in meta and not isinstance(meta['id'], str):
        errors.append("theme_json.meta.id must be a string")
    
    if 'name' in meta and not isinstance(meta['name'], str):
        errors.append("theme_json.meta.name must be a string")
    
    if 'version' in meta and not isinstance(meta['version'], str):
        errors.append("theme_json.meta.version must be a string")
    
    if 'category' in meta and not isinstance(meta['category'], str):
        errors.append("theme_json.meta.category must be a string")
    
    # Optional: description
    if 'description' in meta and not isinstance(meta['description'], str):
        errors.append("theme_json.meta.description must be a string")
    
    # Optional: tags
    if 'tags' in meta:
        if not isinstance(meta['tags'], list):
            errors.append("theme_json.meta.tags must be a list")
        elif not all(isinstance(tag, str) for tag in meta['tags']):
            errors.append("theme_json.meta.tags must contain only strings")
    
    return errors


def _validate_tokens(tokens: Any) -> List[str]:
    """Validate design tokens."""
    errors = []
    
    if not isinstance(tokens, dict):
        return ["theme_json.tokens must be a dictionary"]
    
    # Required token categories
    required = ['colors', 'typography', 'spacing', 'radius', 'shadows', 'motion', 'breakpoints', 'zIndex']
    for category in required:
        if category not in tokens:
            errors.append(f"theme_json.tokens.{category} is required")
    
    # Validate colors
    if 'colors' in tokens:
        errors.extend(_validate_colors(tokens['colors']))
    
    # Validate typography
    if 'typography' in tokens:
        errors.extend(_validate_typography(tokens['typography']))
    
    # Validate spacing
    if 'spacing' in tokens:
        errors.extend(_validate_token_dict(tokens['spacing'], 'spacing'))
    
    # Validate radius
    if 'radius' in tokens:
        errors.extend(_validate_token_dict(tokens['radius'], 'radius'))
    
    # Validate shadows
    if 'shadows' in tokens:
        errors.extend(_validate_token_dict(tokens['shadows'], 'shadows'))
    
    # Validate motion
    if 'motion' in tokens:
        errors.extend(_validate_motion(tokens['motion']))
    
    # Validate breakpoints
    if 'breakpoints' in tokens:
        errors.extend(_validate_token_dict(tokens['breakpoints'], 'breakpoints'))
    
    # Validate zIndex
    if 'zIndex' in tokens:
        errors.extend(_validate_z_index(tokens['zIndex']))
    
    return errors


def _validate_colors(colors: Any) -> List[str]:
    """Validate color tokens."""
    errors = []
    
    if not isinstance(colors, dict):
        return ["theme_json.tokens.colors must be a dictionary"]
    
    # Required color tokens
    required = [
        'primary', 'primaryMuted',
        'secondary', 'secondaryMuted',
        'success', 'warning', 'error', 'info',
        'background', 'surface', 'textPrimary', 'border'
    ]
    
    for field in required:
        if field not in colors:
            errors.append(f"theme_json.tokens.colors.{field} is required")
        elif not isinstance(colors[field], str):
            errors.append(f"theme_json.tokens.colors.{field} must be a string")
    
    return errors


def _validate_typography(typography: Any) -> List[str]:
    """Validate typography tokens."""
    errors = []
    
    if not isinstance(typography, dict):
        return ["theme_json.tokens.typography must be a dictionary"]
    
    # Required fields
    if 'fontFamily' not in typography:
        errors.append("theme_json.tokens.typography.fontFamily is required")
    elif not isinstance(typography['fontFamily'], dict):
        errors.append("theme_json.tokens.typography.fontFamily must be a dictionary")
    else:
        if 'primary' not in typography['fontFamily']:
            errors.append("theme_json.tokens.typography.fontFamily.primary is required")
    
    if 'fontSize' not in typography:
        errors.append("theme_json.tokens.typography.fontSize is required")
    elif not isinstance(typography['fontSize'], dict):
        errors.append("theme_json.tokens.typography.fontSize must be a dictionary")
    
    if 'fontWeight' not in typography:
        errors.append("theme_json.tokens.typography.fontWeight is required")
    elif not isinstance(typography['fontWeight'], dict):
        errors.append("theme_json.tokens.typography.fontWeight must be a dictionary")
    
    if 'lineHeight' not in typography:
        errors.append("theme_json.tokens.typography.lineHeight is required")
    elif not isinstance(typography['lineHeight'], dict):
        errors.append("theme_json.tokens.typography.lineHeight must be a dictionary")
    
    return errors


def _validate_motion(motion: Any) -> List[str]:
    """Validate motion tokens."""
    errors = []
    
    if not isinstance(motion, dict):
        return ["theme_json.tokens.motion must be a dictionary"]
    
    if 'duration' not in motion:
        errors.append("theme_json.tokens.motion.duration is required")
    elif not isinstance(motion['duration'], dict):
        errors.append("theme_json.tokens.motion.duration must be a dictionary")
    
    if 'easing' not in motion:
        errors.append("theme_json.tokens.motion.easing is required")
    elif not isinstance(motion['easing'], dict):
        errors.append("theme_json.tokens.motion.easing must be a dictionary")
    
    return errors


def _validate_z_index(z_index: Any) -> List[str]:
    """Validate zIndex tokens."""
    errors = []
    
    if not isinstance(z_index, dict):
        return ["theme_json.tokens.zIndex must be a dictionary"]
    
    # Check that values are integers
    for key, value in z_index.items():
        if not isinstance(value, int):
            errors.append(f"theme_json.tokens.zIndex.{key} must be an integer")
    
    return errors


def _validate_token_dict(token_dict: Any, category: str) -> List[str]:
    """Validate a generic token dictionary."""
    errors = []
    
    if not isinstance(token_dict, dict):
        errors.append(f"theme_json.tokens.{category} must be a dictionary")
    
    return errors


def _validate_modes(modes: Any) -> List[str]:
    """Validate theme modes."""
    errors = []
    
    if not isinstance(modes, dict):
        return ["theme_json.modes must be a dictionary"]
    
    # Each mode should have name, label, and tokens
    for mode_name, mode_data in modes.items():
        if not isinstance(mode_data, dict):
            errors.append(f"theme_json.modes.{mode_name} must be a dictionary")
            continue
        
        if 'name' not in mode_data:
            errors.append(f"theme_json.modes.{mode_name}.name is required")
        
        if 'label' not in mode_data:
            errors.append(f"theme_json.modes.{mode_name}.label is required")
        
        if 'tokens' not in mode_data:
            errors.append(f"theme_json.modes.{mode_name}.tokens is required")
        elif not isinstance(mode_data['tokens'], dict):
            errors.append(f"theme_json.modes.{mode_name}.tokens must be a dictionary")
    
    return errors


def get_validation_summary(theme_json: Dict[str, Any]) -> str:
    """
    Get a human-readable validation summary.
    
    Returns:
        Summary string with validation results
    """
    try:
        validate_theme_json(theme_json)
        return "✓ Theme JSON is valid"
    except ValidationError as e:
        errors = e.messages if hasattr(e, 'messages') else [str(e)]
        return f"✗ Theme JSON validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
