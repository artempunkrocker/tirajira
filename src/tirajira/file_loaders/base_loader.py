"""
Base class for file loaders with common functionality.
"""

from abc import ABC

from ..utils.path_validation import validate_file_path
from .base import FileLoader


class BaseFileLoader(FileLoader, ABC):
    """Base class for file loaders with common functionality."""

    def _validate_and_open_file(self, file_path: str, mode: str = "r", **kwargs):
        """
        Validates file path and opens the file.

        Args:
            file_path: Path to the file
            mode: File opening mode
            **kwargs: Additional arguments for open()

        Returns:
            Opened file object

        Raises:
            ValueError: If path represents a directory traversal attempt
            FileNotFoundError: If file does not exist
        """
        # Validate file path to prevent directory traversal attacks
        validated_path = validate_file_path(file_path)
        return open(str(validated_path), mode, **kwargs)

    def _handle_generic_exception(self, e: Exception, context: str = "") -> Exception:
        """
        Handles generic exceptions by wrapping them in more descriptive messages.

        Args:
            e: Exception to handle
            context: Context where exception occurred

        Returns:
            Handled exception
        """
        if context:
            message = f"{context}: {str(e)}"
        else:
            message = f"Error reading file: {str(e)}"
        exc = Exception(message)
        exc.__cause__ = e
        return exc
