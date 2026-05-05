"""
Utilities for safe file path validation.
"""

import os
from pathlib import Path
from typing import Union


def is_safe_path(basedir: Union[str, Path], path: Union[str, Path]) -> bool:
    """
    Checks that the path is inside the base directory (prevents
    directory traversal).

    Args:
        basedir: Base directory (e.g., current working directory)
        path: Path to check

    Returns:
        True if path is safe, False if it's a directory traversal attempt
    """
    # Convert to Path objects and normalize paths
    basedir = Path(basedir).resolve()
    path = Path(path).resolve()

    # Check that the path is inside the base directory
    try:
        path.relative_to(basedir)
        return True
    except ValueError:
        # If path is not inside basedir, ValueError will be raised
        return False


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validates file path, preventing directory traversal attacks.

    Args:
        file_path: Path to file for validation

    Returns:
        Normalized Path object

    Raises:
        ValueError: If path represents a directory traversal attempt
        FileNotFoundError: If file does not exist
    """
    # Convert to Path object and normalize path
    path = Path(file_path).resolve()

    # Get current working directory as base
    basedir = Path.cwd().resolve()

    # Check that path is inside the base directory
    if not is_safe_path(basedir, path):
        raise ValueError(f"Path '{file_path}' is outside the allowed directory")

    # Check file existence
    # (using os.path.exists for compatibility with mocks)
    if not os.path.exists(str(path)):
        raise FileNotFoundError(f"File {file_path} not found.")

    return path
