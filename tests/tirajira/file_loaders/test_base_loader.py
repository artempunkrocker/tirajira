"""
Tests for BaseFileLoader.
"""

import os
from typing import Any, Dict, List

import pytest

from src.tirajira.file_loaders.base_loader import BaseFileLoader


class TestableBaseFileLoader(BaseFileLoader):
    """Testable implementation of BaseFileLoader."""

    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Implementation of abstract method for testing."""
        pass


class TestBaseFileLoader:
    """Tests for BaseFileLoader."""

    def test_validate_and_open_file_success(self):
        """Test successful file opening."""
        tmp_file_path = "test_temp_file.txt"
        try:
            with open(tmp_file_path, "w") as f:
                f.write("test content")

            loader = TestableBaseFileLoader()

            with loader._validate_and_open_file(tmp_file_path) as f:
                content = f.read()

            assert content == "test content"
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    def test_validate_and_open_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            loader = TestableBaseFileLoader()
            loader._validate_and_open_file("non_existent_file.txt")

    def test_handle_generic_exception(self):
        """Test handling of generic exception."""
        loader = TestableBaseFileLoader()

        original_exception = Exception("Original error")

        handled_exception = loader._handle_generic_exception(original_exception)

        assert "Error reading file:" in str(handled_exception)
        assert "Original error" in str(handled_exception)

        assert handled_exception.__cause__ is original_exception

    def test_handle_generic_exception_with_context(self):
        """Test handling of generic exception with context."""
        loader = TestableBaseFileLoader()

        original_exception = Exception("Original error")

        handled_exception = loader._handle_generic_exception(
            original_exception, "Error parsing"
        )

        assert "Error parsing:" in str(handled_exception)
        assert "Original error" in str(handled_exception)

        assert handled_exception.__cause__ is original_exception
