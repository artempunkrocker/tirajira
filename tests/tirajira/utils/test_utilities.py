"""
Tests for TiraJira project utilities.
"""

# Tests for dot notation utilities
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tirajira.utils.dot_notation_utils import convert_dot_notation_to_nested_dict
from tirajira.utils.flatten_utils import ListHandlingStrategy, flatten_dict
from tirajira.utils.path_validation import is_safe_path, validate_file_path


def test_convert_dot_notation_to_nested_dict_simple():
    """Test: conversion of a simple dictionary without dot notation."""
    flat_dict = {"key": "value"}
    expected = {"key": "value"}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_single_level():
    """Test: conversion of a dictionary with single dot notation."""
    flat_dict = {"project.key": "PROJ"}
    expected = {"project": {"key": "PROJ"}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_multiple_levels():
    """Test: conversion of a dictionary with multi-level dot notation."""
    flat_dict = {"project.key": "PROJ", "issuetype.name": "Task"}
    expected = {"project": {"key": "PROJ"}, "issuetype": {"name": "Task"}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_deep_nesting():
    """Test: conversion of a dictionary with deep nesting."""
    flat_dict = {"project.category.type.name": "Software"}
    expected = {"project": {"category": {"type": {"name": "Software"}}}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_mixed_keys():
    """Test: conversion of a dictionary with mixed keys (with and without dots)."""
    flat_dict = {
        "summary": "Test task",
        "project.key": "PROJ",
        "issuetype.name": "Task",
    }
    expected = {
        "summary": "Test task",
        "project": {"key": "PROJ"},
        "issuetype": {"name": "Task"},
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_empty_dict():
    """Test: conversion of an empty dictionary."""
    flat_dict = {}
    expected = {}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_keys_with_numbers():
    """Test: conversion of a dictionary with keys containing numbers."""
    flat_dict = {"customfield_10001": "Value"}
    expected = {"customfield_10001": "Value"}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_complex_example():
    """Test: conversion of a dictionary with a complex example from documentation."""
    flat_dict = {
        "project": {"key": "PROJ"},
        "issuetype": {"name": "Task"},
        "customfield_10001": "Business Value: High",
        "assignee": {"emailAddress": "developer@example.com"},
    }
    expected = {
        "project": {"key": "PROJ"},
        "issuetype": {"name": "Task"},
        "customfield_10001": "Business Value: High",
        "assignee": {"emailAddress": "developer@example.com"},
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


# Tests for validation functionality
def test_convert_dot_notation_to_nested_dict_empty_key():
    """Test: handling of an empty key."""
    flat_dict = {"": "value"}
    with pytest.raises(ValueError, match="Keys cannot be empty strings"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_leading_dot():
    """Test: handling of a key with a leading dot."""
    flat_dict = {".key": "value"}
    with pytest.raises(ValueError, match="Keys cannot start or end with dots"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_trailing_dot():
    """Test: handling of a key with a trailing dot."""
    flat_dict = {"key.": "value"}
    with pytest.raises(ValueError, match="Keys cannot start or end with dots"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_consecutive_dots():
    """Test: handling of a key with consecutive dots."""
    flat_dict = {"key..subkey": "value"}
    with pytest.raises(ValueError, match="Keys cannot contain consecutive dots"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_multiple_consecutive_dots():
    """Test: handling of a key with multiple consecutive dots."""
    flat_dict = {"key...subkey": "value"}
    with pytest.raises(ValueError, match="Keys cannot contain consecutive dots"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_non_string_key():
    """Test: handling of a non-string key."""
    flat_dict = {123: "value"}
    with pytest.raises(TypeError, match="All keys must be strings"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_none_key():
    """Test: handling of a key with None value."""
    flat_dict = {None: "value"}
    with pytest.raises(TypeError, match="All keys must be strings"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_tuple_key():
    """Test: handling of a tuple key."""
    flat_dict = {("a", "b"): "value"}
    with pytest.raises(TypeError, match="All keys must be strings"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_exceeds_max_depth():
    """Test: handling of a key that exceeds the maximum nesting depth."""
    flat_dict = {"a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z": "value"}
    with pytest.raises(ValueError, match="exceeds maximum nesting depth"):
        convert_dot_notation_to_nested_dict(flat_dict, max_depth=10)


def test_convert_dot_notation_to_nested_dict_valid_custom_max_depth():
    """Test: handling of a key with valid depth under custom limitation."""
    flat_dict = {"a.b.c.d.e": "value"}
    expected = {"a": {"b": {"c": {"d": {"e": "value"}}}}}
    result = convert_dot_notation_to_nested_dict(flat_dict, max_depth=10)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_key_with_empty_segments():
    """Test: handling of a key with empty segments after splitting."""
    # This case is covered by other tests, but let's explicitly test it
    flat_dict = {"a..b": "value"}  # Two dots create empty segment
    with pytest.raises(ValueError, match="Keys cannot contain consecutive dots"):
        convert_dot_notation_to_nested_dict(flat_dict)


def test_convert_dot_notation_to_nested_dict_international_characters():
    """Test: conversion of a dictionary with keys containing
    international characters."""
    flat_dict = {
        "project.key": "PROJECT",
        "type.name": "task",
        "project2.key": "project",
        "key.project": "PROJECT",
    }
    expected = {
        "project": {"key": "PROJECT"},
        "type": {"name": "task"},
        "project2": {"key": "project"},
        "key": {"project": "PROJECT"},
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_numeric_and_special_keys():
    """Test: conversion of a dictionary with numeric keys and special characters."""
    flat_dict = {
        "key_123.value": "numeric_part",
        "key-with-dashes.value": "dash_part",
        "key with spaces.value": "space_part",
        "key@domain.value": "at_sign_part",
        "key#tag.value": "hash_part",
        "key$value.value": "dollar_part",
        "key_value.value": "underscore_part",
    }
    expected = {
        "key_123": {"value": "numeric_part"},
        "key-with-dashes": {"value": "dash_part"},
        "key with spaces": {"value": "space_part"},
        "key@domain": {"value": "at_sign_part"},
        "key#tag": {"value": "hash_part"},
        "key$value": {"value": "dollar_part"},
        "key_value": {"value": "underscore_part"},
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_deep_nesting_with_unicode():
    """Test: conversion of a dictionary with deep nesting and unicode characters."""
    flat_dict = {"α.β.γ.δ.ε.ζ.η.θ": "unicode_chain"}
    expected = {"α": {"β": {"γ": {"δ": {"ε": {"ζ": {"η": {"θ": "unicode_chain"}}}}}}}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_special_characters_with_dots():
    """Test: conversion of a dictionary with special characters and dots in keys."""
    flat_dict = {
        "key.with.dots.in.name": "dot_value",
        "key[with]brackets": "bracket_value",
        "key(with)parentheses": "parentheses_value",
        "key{with}braces": "braces_value",
    }
    expected = {
        "key": {"with": {"dots": {"in": {"name": "dot_value"}}}},
        "key[with]brackets": "bracket_value",
        "key(with)parentheses": "parentheses_value",
        "key{with}braces": "braces_value",
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_deep_nesting_with_special_chars():
    """Test: conversion of a dictionary with deep nesting and special characters."""
    flat_dict = {"a-b.c_d.e@f.g#h": "special_chain"}
    expected = {"a-b": {"c_d": {"e@f": {"g#h": "special_chain"}}}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_flatten_dict_indexed_expansion_default():
    """Test: conversion of a dictionary with list expansion by indices (default)"""
    # Prepare test data
    data = {"a": {"b": 1, "c": [2, 3, 4]}, "d": [{"e": 5}, {"f": 6}]}

    # Perform conversion
    result = flatten_dict(data)

    # Check result
    expected = {"a.b": 1, "a.c.0": 2, "a.c.1": 3, "a.c.2": 4, "d.0.e": 5, "d.1.f": 6}

    assert result == expected


def test_flatten_dict_indexed_expansion_explicit():
    """Test: conversion of a dictionary with explicit specification of
    list expansion strategy"""
    # Prepare test data
    data = {"a": {"b": 1, "c": [2, 3]}}

    # Perform conversion
    result = flatten_dict(data, list_handling=ListHandlingStrategy.INDEXED_EXPANSION)

    # Check result
    expected = {"a.b": 1, "a.c.0": 2, "a.c.1": 3}

    assert result == expected


def test_flatten_dict_json_serialization():
    """Test: conversion of a dictionary with list serialization to JSON"""
    # Prepare test data
    data = {"a": {"b": 1, "c": [2, 3, 4]}, "d": [{"e": 5}, {"f": 6}]}

    # Perform conversion
    result = flatten_dict(data, list_handling=ListHandlingStrategy.JSON_SERIALIZATION)

    # Check result
    expected = {
        "a.b": 1,
        "a.c": json.dumps([2, 3, 4], ensure_ascii=False),
        "d": json.dumps([{"e": 5}, {"f": 6}], ensure_ascii=False),
    }

    assert result == expected


def test_flatten_dict_with_custom_separator():
    """Test: conversion of a dictionary with a custom separator"""
    # Prepare test data
    data = {"a": {"b": 1, "c": [2, 3]}}

    # Perform conversion
    result = flatten_dict(data, sep="_")

    # Check result
    expected = {"a_b": 1, "a_c_0": 2, "a_c_1": 3}

    assert result == expected


def test_flatten_dict_empty_data():
    """Test: conversion of an empty dictionary"""
    # Prepare test data
    data = {}

    # Perform conversion
    result = flatten_dict(data)

    # Check result
    expected = {}

    assert result == expected


def test_flatten_dict_nested_dictionaries_only():
    """Test: conversion of a dictionary with only nested dictionaries (no lists)"""
    # Prepare test data
    data = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}

    # Perform conversion
    result = flatten_dict(data)

    # Check result
    expected = {"a.b.c": 1, "a.b.d": 2, "a.e": 3, "f": 4}

    assert result == expected


def test_flatten_dict_complex_structure():
    """Test: conversion of a complex data structure"""
    # Prepare test data
    data = {
        "project": {"key": "PROJ", "name": "Test Project"},
        "issues": [
            {
                "id": 1,
                "summary": "First issue",
                "assignee": {"name": "John Doe", "email": "john.doe@example.com"},
                "labels": ["bug", "urgent"],
            },
            {"id": 2, "summary": "Second issue", "labels": ["feature"]},
        ],
        "metadata": {"total_issues": 2, "created_at": "2023-12-01T15:30:45"},
    }

    # Perform conversion with indexed expansion
    result_indexed = flatten_dict(
        data, list_handling=ListHandlingStrategy.INDEXED_EXPANSION
    )

    # Check result
    expected_indexed = {
        "project.key": "PROJ",
        "project.name": "Test Project",
        "issues.0.id": 1,
        "issues.0.summary": "First issue",
        "issues.0.assignee.name": "John Doe",
        "issues.0.assignee.email": "john.doe@example.com",
        "issues.0.labels.0": "bug",
        "issues.0.labels.1": "urgent",
        "issues.1.id": 2,
        "issues.1.summary": "Second issue",
        "issues.1.labels.0": "feature",
        "metadata.total_issues": 2,
        "metadata.created_at": "2023-12-01T15:30:45",
    }

    assert result_indexed == expected_indexed

    # Perform conversion with JSON serialization
    result_json = flatten_dict(
        data, list_handling=ListHandlingStrategy.JSON_SERIALIZATION
    )

    # Check result
    expected_json = {
        "project.key": "PROJ",
        "project.name": "Test Project",
        "issues": json.dumps(
            [
                {
                    "id": 1,
                    "summary": "First issue",
                    "assignee": {"name": "John Doe", "email": "john.doe@example.com"},
                    "labels": ["bug", "urgent"],
                },
                {"id": 2, "summary": "Second issue", "labels": ["feature"]},
            ],
            ensure_ascii=False,
        ),
        "metadata.total_issues": 2,
        "metadata.created_at": "2023-12-01T15:30:45",
    }

    assert result_json == expected_json


def test_is_safe_path_valid_paths():
    """Test: checking safe paths."""
    # Get the current working directory
    cwd = Path.cwd()

    # Check that paths inside the current directory are considered safe
    assert is_safe_path(cwd, cwd / "file.txt")
    assert is_safe_path(cwd, cwd / "subdir" / "file.txt")
    assert is_safe_path(cwd, cwd / "subdir1" / "subdir2" / "file.txt")


def test_is_safe_path_invalid_paths():
    """Test: checking unsafe paths (directory traversal)."""
    # Get the current working directory
    cwd = Path.cwd()

    # Check that paths outside the current directory are considered unsafe
    assert not is_safe_path(cwd, cwd.parent / "file.txt")
    assert not is_safe_path(cwd, cwd / ".." / ".." / "etc" / "passwd")
    assert not is_safe_path(cwd, Path("/etc/passwd"))
    assert not is_safe_path(cwd, Path("../sensitive_file.txt"))


def test_validate_file_path_safe_path():
    """Test: validation of a safe path to an existing file."""
    # Create a temporary file in the current directory for testing
    with tempfile.NamedTemporaryFile(dir=".", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    try:
        # Check that validation passes successfully for a safe path
        validated_path = validate_file_path(tmp_file_path)
        assert isinstance(validated_path, Path)
        assert str(validated_path) == os.path.abspath(tmp_file_path)
    finally:
        os.unlink(tmp_file_path)


def test_validate_file_path_directory_traversal():
    """Test: validation of a path with a directory traversal attempt."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    try:
        with pytest.raises(ValueError, match="is outside the allowed directory"):
            validate_file_path(f"../{os.path.basename(tmp_file_path)}")
    finally:
        os.unlink(tmp_file_path)


def test_validate_file_path_nonexistent_file():
    """Test: validation of a path to a non-existent file."""
    # Check that validation throws FileNotFoundError for a non-existent file
    with pytest.raises(FileNotFoundError):
        validate_file_path("nonexistent_file.txt")


@patch("os.path.exists", return_value=True)
def test_validate_file_path_with_mock(mock_exists):
    """Test: validation of a path using a mock."""
    # This test checks compatibility with existing tests,
    # which use mocks for os.path.exists

    # Check that validation passes successfully for a safe path
    validated_path = validate_file_path("test_file.txt")
    assert isinstance(validated_path, Path)
