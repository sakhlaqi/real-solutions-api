"""
Utility functions for tenant app.
"""

import copy


def deep_merge_tokens(base, overrides):
    """
    Deep merge token overrides into base tokens.
    
    Args:
        base (dict): Base token dictionary
        overrides (dict): Token overrides to apply
    
    Returns:
        dict: Merged token dictionary
    
    Example:
        base = {
            'colors': {'primary': '#000', 'secondary': '#fff'},
            'spacing': {'small': '8px'}
        }
        overrides = {
            'colors': {'primary': '#ff0000'}
        }
        result = {
            'colors': {'primary': '#ff0000', 'secondary': '#fff'},
            'spacing': {'small': '8px'}
        }
    """
    if not isinstance(base, dict) or not isinstance(overrides, dict):
        # If either is not a dict, override wins
        return copy.deepcopy(overrides) if overrides else copy.deepcopy(base)
    
    # Start with deep copy of base
    result = copy.deepcopy(base)
    
    # Recursively merge overrides
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Both are dicts - recurse
            result[key] = deep_merge_tokens(result[key], value)
        else:
            # Override value (handles primitives, lists, and new keys)
            result[key] = copy.deepcopy(value)
    
    return result


def calculate_token_diff(base, modified):
    """
    Calculate the difference between base and modified tokens.
    Returns only the keys that are different in modified.
    
    Args:
        base (dict): Base token dictionary
        modified (dict): Modified token dictionary
    
    Returns:
        dict: Dictionary containing only changed tokens
    
    Example:
        base = {
            'colors': {'primary': '#000', 'secondary': '#fff'},
            'spacing': {'small': '8px'}
        }
        modified = {
            'colors': {'primary': '#ff0000', 'secondary': '#fff'},
            'spacing': {'small': '8px'}
        }
        result = {
            'colors': {'primary': '#ff0000'}
        }
    """
    if not isinstance(base, dict) or not isinstance(modified, dict):
        # If types differ, return modified
        return modified if modified != base else {}
    
    diff = {}
    
    # Check all keys in modified
    for key, value in modified.items():
        if key not in base:
            # New key - include it
            diff[key] = copy.deepcopy(value)
        elif isinstance(value, dict) and isinstance(base[key], dict):
            # Both are dicts - recurse
            nested_diff = calculate_token_diff(base[key], value)
            if nested_diff:
                diff[key] = nested_diff
        elif value != base[key]:
            # Values differ - include it
            diff[key] = copy.deepcopy(value)
    
    return diff
