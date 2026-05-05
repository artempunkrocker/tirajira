"""
Utilities for working with dot notation in dictionary keys.
"""

from functools import lru_cache
from typing import Any, Dict, List


# Cache for storing key parsing results
@lru_cache(maxsize=1024)
def _cached_split_key(key: str) -> tuple:
    """Cached key splitting by dots."""
    return tuple(key.split("."))


def convert_dot_notation_to_nested_dict(
    flat_dict: Dict[str, Any], max_depth: int = 50
) -> Dict[str, Any]:
    """Converts a flat dictionary with dot notation to a nested dictionary.

    Args:
        flat_dict: Flat dictionary with dot notation in keys
        max_depth: Maximum nesting depth (default 50)

    Returns:
        Nested dictionary

    Raises:
        TypeError: If keys are not strings
        ValueError: If keys contain invalid characters or exceed
            maximum depth

    Example:
        >>> convert_dot_notation_to_nested_dict({'project.key': 'PROJ',
                                                 'issuetype.name': 'Task'})
        {'project': {'key': 'PROJ'}, 'issuetype': {'name': 'Task'}}
    """
    nested_dict: Dict[str, Any] = {}

    # Validate all keys before processing
    for key in flat_dict.keys():
        _validate_dot_notation_key(key, max_depth)

    # Split keys into two groups for optimized processing
    dotted_keys = {}
    direct_keys = {}

    for key, value in flat_dict.items():
        # Process keys with dot notation
        if "." in key:
            dotted_keys[key] = value
        else:
            # Keys without dots are added directly
            direct_keys[key] = value

    # Add keys without dots directly
    nested_dict.update(direct_keys)

    # Optimized processing of keys with dots
    # Sort by keys to group similar prefixes
    sorted_dotted_items = sorted(dotted_keys.items())

    for key, value in sorted_dotted_items:
        __process_dotted_key(key, value, nested_dict)

    return nested_dict


def _validate_dot_notation_key(key: str, max_depth: int = 50) -> List[str]:
    """Validates a key with dot notation and returns its parts.

    Args:
        key: Key to validate
        max_depth: Maximum nesting depth

    Returns:
        List of key parts

    Raises:
        TypeError: If key is not a string
        ValueError: If key contains invalid characters or structure
    """
    if not isinstance(key, str):
        raise TypeError(f"All keys must be strings, got {type(key).__name__}: {key}")

    if not key:
        raise ValueError("Keys cannot be empty strings")

    if key.startswith(".") or key.endswith("."):
        raise ValueError(f"Keys cannot start or end with dots: '{key}'")

    if ".." in key:
        raise ValueError(f"Keys cannot contain consecutive dots: '{key}'")

    key_parts = key.split(".")

    if len(key_parts) > max_depth:
        raise ValueError(f"Key '{key}' exceeds maximum nesting depth of {max_depth}")

    if any(not part for part in key_parts):
        raise ValueError(f"Keys cannot contain empty segments: '{key}'")

    return key_parts


def __process_dotted_key(key: str, value: Any, nested_dict: Dict[str, Any]) -> None:
    """Processes a key with dot notation, creating nested dictionaries."""
    # Split key by dots using cache
    key_parts = _cached_split_key(key)
    current_dict = nested_dict

    # Create nested dictionaries for all parts except the last one
    for part in key_parts[:-1]:
        if part not in current_dict:
            current_dict[part] = {}
        current_dict = current_dict[part]

    # Set value for the last part
    current_dict[key_parts[-1]] = value
