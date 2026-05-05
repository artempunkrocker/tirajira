"""Standardized exception handler decorator for file loaders."""

import csv
import json
import xml.etree.ElementTree as ET
from functools import wraps
from typing import Any, Callable, Optional

import yaml


def handle_loader_exceptions(
    func: Optional[Callable[..., Any]] = None, format_name: str = "file"
) -> Callable[..., Any]:
    """
    Decorator for standardized exception handling in file loaders.

    Args:
        func: Function to decorate
        format_name: Name of the file format for error messages

    Returns:
        Decorated function with standardized exception handling
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except (
                json.JSONDecodeError,
                csv.Error,
                yaml.YAMLError,
                ET.ParseError,
            ) as e:
                raise ValueError(f"Error parsing {format_name}: {str(e)}") from e
            except ValueError:
                raise
            except FileNotFoundError:
                raise
            except OSError as e:
                # For OS-level errors, use the same format as the old implementation
                raise Exception(f"Error reading file: {str(e)}") from e
            except Exception as e:
                # Check for Excel-specific exceptions
                if e.__class__.__name__ == "InvalidFileException":
                    # Handle InvalidFileException from openpyxl as a parsing error
                    raise ValueError(f"Error parsing {format_name}: {str(e)}") from e
                # For all other exceptions, use the same format as the old
                # implementation
                raise Exception(f"Error reading file: {str(e)}") from e

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)
