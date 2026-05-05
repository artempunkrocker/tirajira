"""
Loader for issues from CSV files.
"""

import csv
from typing import Any, Dict, List

from ..utils.dot_notation_utils import convert_dot_notation_to_nested_dict
from .base_loader import BaseFileLoader
from .exception_handler import handle_loader_exceptions


class CsvFileLoader(BaseFileLoader):
    """Loader for issues from CSV files with dot notation support in headers."""

    @handle_loader_exceptions(format_name="CSV file")
    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Loads issues from CSV file with dot notation support in headers."""
        issues = []
        with self._validate_and_open_file(file_path, "r", encoding="utf-8") as f:
            # Determine CSV file dialect
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)

            reader = csv.DictReader(f, dialect=dialect)

            # Check that file is not empty
            if reader.fieldnames is None:
                raise Exception("Error reading file: CSV file is empty or corrupted")

            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue

                # Filter out empty values
                filtered_row = {
                    k: v for k, v in row.items() if v is not None and v != ""
                }

                # Convert flat dictionary with dot notation to nested dictionary
                nested_dict = convert_dot_notation_to_nested_dict(filtered_row)

                # Process linking information if present
                if isinstance(nested_dict, dict) and "linking" in nested_dict:
                    linking_info = nested_dict.pop("linking")
                    if isinstance(linking_info, (dict, list)):
                        if isinstance(linking_info, dict) and all(
                            isinstance(k, str) and k.isdigit()
                            for k in linking_info.keys()
                        ):
                            sorted_items = sorted(
                                linking_info.items(), key=lambda x: int(x[0])
                            )
                            linking_info = [v for _, v in sorted_items]
                        # Add linking information directly to the issue
                        nested_dict["linking"] = linking_info

                issues.append(nested_dict)

        return issues
