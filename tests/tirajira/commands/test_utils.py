"""
Tests for utility functions with path validation in commands/utils.py
"""

import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from tirajira.commands.utils import load_json_report, load_yaml_report


def test_load_json_report_success_with_path_validation():
    """Test successful loading of JSON reports with path validation."""
    # Create a temporary file in the current directory
    with tempfile.NamedTemporaryFile(
        mode="w", dir=".", suffix=".json", delete=False
    ) as tmp_file:
        json_content = {"tasks": [{"summary": "Test task"}]}
        json.dump(json_content, tmp_file)
        safe_file_path = tmp_file.name

    try:
        # Use basename as valid relative path
        relative_path = os.path.basename(safe_file_path)

        # Load the JSON report
        result = load_json_report(relative_path)

        # Check that the result is correct
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["summary"] == "Test task"
    finally:
        # Cleanup
        os.unlink(safe_file_path)


def test_load_json_report_directory_traversal_prevention():
    """Test directory traversal prevention in JSON reports."""
    # Create a temporary file in the current directory
    with tempfile.NamedTemporaryFile(
        mode="w", dir=".", suffix=".json", delete=False
    ) as tmp_file:
        json_content = {"tasks": []}
        json.dump(json_content, tmp_file)
        safe_file_path = tmp_file.name

    try:
        # Create a path traversal attempt
        traversal_path = f"../{os.path.basename(safe_file_path)}"

        # Attempt to load the JSON report - should fail due to path validation
        with pytest.raises(Exception) as exc_info:
            load_json_report(traversal_path)

            # Check that the error message is correct
            assert "Path" in str(exc_info.value)
            assert "outside the allowed directory" in str(exc_info.value)
    finally:
        # Cleanup
        os.unlink(safe_file_path)


def test_load_json_report_file_not_found():
    """Test file not found errors in JSON reports."""
    # Try to load a non-existent file
    with pytest.raises(Exception) as exc_info:
        load_json_report("nonexistent.json")

    # Check that the error message is correct
    assert "File nonexistent.json not found" in str(exc_info.value)


def test_load_json_report_invalid_json():
    """Test invalid JSON in JSON reports."""
    # Create a temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(
        mode="w", dir=".", suffix=".json", delete=False
    ) as tmp_file:
        tmp_file.write('{"tasks": [{invalid json]}')
        safe_file_path = tmp_file.name

    try:
        # Use basename as valid relative path
        relative_path = os.path.basename(safe_file_path)

        # Attempt to load the JSON report - should fail due to invalid JSON
        with pytest.raises(ValueError) as exc_info:
            load_json_report(relative_path)

        # Check that the error message is correct
        assert "Error parsing JSON report file" in str(exc_info.value)
    finally:
        # Cleanup
        os.unlink(safe_file_path)


def test_load_yaml_report_file_not_found():
    """Test file not found errors in YAML reports."""
    # Try to load a non-existent file
    with pytest.raises(Exception) as exc_info:
        load_yaml_report("nonexistent.yaml")

    # Check that the error message is correct
    assert "File nonexistent.yaml not found" in str(exc_info.value)


def test_load_yaml_report_invalid_yaml():
    """Test invalid YAML in YAML reports."""
    # Create a temporary file with invalid YAML
    with tempfile.NamedTemporaryFile(
        mode="w", dir=".", suffix=".yaml", delete=False
    ) as tmp_file:
        tmp_file.write("""
tasks:
  - summary: Test task
    invalid: : yaml
""")
        safe_file_path = tmp_file.name

    try:
        # Use basename as valid relative path
        relative_path = os.path.basename(safe_file_path)

        # Attempt to load the YAML report - should fail due to invalid YAML
        with pytest.raises(ValueError) as exc_info:
            load_yaml_report(relative_path)

        # Check that the error message is correct
        assert "Error parsing YAML report file" in str(exc_info.value)
    finally:
        # Cleanup
        os.unlink(safe_file_path)


def test_load_yaml_report_invalid_format():
    """Test invalid format in YAML reports."""
    # Create a temporary file with invalid format (array instead of object)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=".", suffix=".yaml", delete=False
    ) as tmp_file:
        yaml_content = """
- summary: Test task
"""
        tmp_file.write(yaml_content)
        safe_file_path = tmp_file.name

    try:
        # Use basename as valid relative path
        relative_path = os.path.basename(safe_file_path)

        # Patch yaml.safe_load to return specific data
        with patch("tirajira.commands.utils.yaml.safe_load") as mock_yaml_load:
            # Array instead of object
            mock_yaml_load.return_value = [{"summary": "Test task"}]

            # Attempt to load the YAML report - should fail due to invalid format
            with pytest.raises(Exception) as exc_info:
                load_yaml_report(relative_path)

            # Check that the error message is correct
            assert "YAML report file must contain an object" in str(exc_info.value)
    finally:
        # Cleanup
        os.unlink(safe_file_path)


def test_load_yaml_report_with_file_handler():
    """Test loading YAML reports with file handler parameter."""
    # Mock file handler with valid YAML content
    mock_file_handler = Mock()

    # Patch yaml.safe_load to return specific data
    with patch("tirajira.commands.utils.yaml.safe_load") as mock_yaml_load:
        mock_yaml_load.return_value = {"tasks": [{"summary": "Test task"}]}

        # Load the YAML report with file handler
        result = load_yaml_report("any_path.yaml", file_handler=mock_file_handler)

        # Check that the result is correct
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["summary"] == "Test task"

        # Check that yaml.safe_load was called with the file handler
        mock_yaml_load.assert_called_once_with(mock_file_handler)
