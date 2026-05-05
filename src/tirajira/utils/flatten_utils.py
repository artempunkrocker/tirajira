"""
Utilities for converting nested dictionaries to flat ones.
"""

import json
from collections.abc import MutableMapping
from enum import Enum
from typing import Any, Dict


class ListHandlingStrategy(Enum):
    """Strategies for handling lists during dictionary conversion."""

    INDEXED_EXPANSION = "indexed_expansion"  # Expansion with indices (for CSV)
    JSON_SERIALIZATION = "json_serialization"  # Serialization to JSON (for Excel)


def _handle_list_indexed_expansion(
    items: list, lst: list, key: str, sep: str, list_handling: ListHandlingStrategy
) -> None:
    """Handle list processing with indexed expansion strategy."""
    for i, item in enumerate(lst):
        if isinstance(item, dict):
            # Recursively convert dictionaries in the list
            items.extend(
                flatten_dict(item, f"{key}{sep}{i}", sep, list_handling).items()
            )
        else:
            # For simple values in the list, just add them
            items.append((f"{key}{sep}{i}", item))


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = "",
    sep: str = ".",
    list_handling: ListHandlingStrategy = ListHandlingStrategy.INDEXED_EXPANSION,
) -> Dict[str, Any]:
    """
    Converts a nested dictionary to a flat one by joining keys with a separator.

    Supports two list handling strategies:
    1. INDEXED_EXPANSION - creates a separate key with index for each list element
       (used in CSV writer)
    2. JSON_SERIALIZATION - serializes the entire list to a JSON string
       (used in Excel writer)

    Args:
        d: Nested dictionary to convert
        parent_key: Parent key (for recursive calls)
        sep: Separator for joining keys
        list_handling: Strategy for handling lists

    Returns:
        Flat dictionary with keys joined by separator

    Examples:
        >>> # Indexed expansion (default)
        >>> flatten_dict({"a": [{"b": 1}, {"c": 2}]})
        {'a.0.b': 1, 'a.1.c': 2}

        >>> # JSON serialization
        >>> flatten_dict({"a": [{"b": 1}, {"c": 2}]},
        ...              list_handling=ListHandlingStrategy.JSON_SERIALIZATION)
        {'a': '[{"b": 1}, {"c": 2}]'}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep, list_handling).items())
        elif isinstance(v, list):
            if list_handling == ListHandlingStrategy.JSON_SERIALIZATION:
                # Convert list to JSON string
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                # For lists, convert each element to a separate field
                # INDEXED_EXPANSION including else case (for compatibility)
                _handle_list_indexed_expansion(items, v, new_key, sep, list_handling)
        else:
            items.append((new_key, v))
    return dict(items)
