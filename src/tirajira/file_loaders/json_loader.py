"""
Loader for issues from JSON files.
"""

import json
from typing import Any, Dict, List

from .base_loader import BaseFileLoader
from .exception_handler import handle_loader_exceptions


class JsonFileLoader(BaseFileLoader):
    """Loader for issues from JSON files."""

    @handle_loader_exceptions(format_name="JSON file")
    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Loads issues from JSON file."""
        with self._validate_and_open_file(file_path, "r", encoding="utf-8") as f:
            issues = json.load(f)

        # Check that data has the correct format
        if not isinstance(issues, list):
            raise ValueError("JSON file must contain an array of issues")

        # Process linking information for each issue
        for issue in issues:
            if isinstance(issue, dict) and "linking" in issue:
                linking_info = issue.pop("linking")
                if isinstance(linking_info, (dict, list)):
                    # Add linking information directly to the issue
                    issue["linking"] = linking_info

        return issues
