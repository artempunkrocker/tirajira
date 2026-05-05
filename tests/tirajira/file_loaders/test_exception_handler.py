import csv
import json

import pytest

from tirajira.file_loaders.exception_handler import handle_loader_exceptions


def test_handle_loader_exceptions_with_json_decode_error():
    """Test: handling JSONDecodeError exception"""

    @handle_loader_exceptions(format_name="JSON file")
    def faulty_function():
        raise json.JSONDecodeError("Invalid JSON", "", 0)

    with pytest.raises(
        ValueError,
        match="Error parsing JSON file: Invalid JSON: line 1 column 1 \\(char 0\\)",
    ):
        faulty_function()


def test_handle_loader_exceptions_with_csv_error():
    """Test: handling csv.Error exception"""

    @handle_loader_exceptions(format_name="CSV file")
    def faulty_function():
        raise csv.Error("CSV parsing error")

    with pytest.raises(ValueError, match=("Error parsing CSV file: CSV parsing error")):
        faulty_function()


def test_handle_loader_exceptions_with_value_error():
    """Test: handling ValueError exception"""

    @handle_loader_exceptions()
    def faulty_function():
        raise ValueError("Value error")

    with pytest.raises(ValueError, match="Value error"):
        faulty_function()


def test_handle_loader_exceptions_with_file_not_found_error():
    """Test: handling FileNotFoundError exception"""

    @handle_loader_exceptions()
    def faulty_function():
        raise FileNotFoundError("File not found")

    with pytest.raises(FileNotFoundError, match="File not found"):
        faulty_function()


def test_handle_loader_exceptions_with_os_error():
    """Test: handling OSError exception"""

    @handle_loader_exceptions(format_name="test file")
    def faulty_function():
        raise OSError("OS error")

    # For backward compatibility, OS errors use the standard format
    with pytest.raises(Exception, match="Error reading file: OS error"):
        faulty_function()


def test_handle_loader_exceptions_with_generic_exception():
    """Test: handling generic Exception exception"""

    @handle_loader_exceptions(format_name="test file")
    def faulty_function():
        raise Exception("Generic error")

    # For backward compatibility, generic exceptions use the standard format
    with pytest.raises(Exception, match="Error reading file: Generic error"):
        faulty_function()


def test_handle_loader_exceptions_success():
    """Test: successful function execution without exceptions"""

    @handle_loader_exceptions()
    def normal_function():
        return "success"

    assert normal_function() == "success"
