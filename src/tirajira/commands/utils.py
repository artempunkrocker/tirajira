"""
Utilities for TiraJira commands.
"""

import json
from typing import Any, Dict, List, Optional, TextIO

import yaml

from ..utils.path_validation import validate_file_path


def load_json_report(
    file_path: str, file_handler: Optional[TextIO] = None
) -> Dict[str, Any]:
    """
    Loads report from JSON file.

    Args:
        file_path: Path to JSON report file
        file_handler: Optional file descriptor

    Returns:
        Dictionary with report data

    Raises:
        ValueError: If file has incorrect format
        Exception: For other file reading errors
    """
    try:
        if file_handler is not None:
            report_data = json.load(file_handler)
        else:
            # Validate file path before opening
            validated_path = validate_file_path(file_path)
            with open(validated_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)

        # Check that data has correct format
        if not isinstance(report_data, dict):
            raise ValueError("JSON report file must contain an object")

        return report_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON report file: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Error reading report file: {str(e)}") from e


def load_yaml_report(
    file_path: str, file_handler: Optional[TextIO] = None
) -> Dict[str, Any]:
    """
    Loads report from YAML file.

    Args:
        file_path: Path to YAML report file
        file_handler: Optional file descriptor

    Returns:
        Dictionary with report data

    Raises:
        ValueError: If file has incorrect format
        Exception: For other file reading errors
    """
    try:
        if file_handler is not None:
            report_data = yaml.safe_load(file_handler)
        else:
            # Validate file path before opening
            validated_path = validate_file_path(file_path)
            with open(validated_path, "r", encoding="utf-8") as f:
                report_data = yaml.safe_load(f)

        # Check that data has correct format
        if not isinstance(report_data, dict):
            raise ValueError("YAML report file must contain an object")

        return report_data
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML report file: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Error reading report file: {str(e)}") from e


def _extract_from_json_yaml_report(task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extracts task from JSON/YAML report."""
    status = task.get("status", "").lower()
    if status == "failure":
        # Extract original task data
        original_data = task.get("issue_data", {})
        if original_data:
            return original_data
        else:
            # If issue_data is not present, save the entire task
            # without service fields
            cleaned_task = {
                key: value
                for key, value in task.items()
                if key not in ["status", "error_message", "processed_at"]
            }
            return cleaned_task
    return None


def _extract_from_csv_excel_report(task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extracts task from CSV/Excel report."""
    status = task.get("tasks.status", "").lower()
    if status == "failure":
        # Extract original task data (fields without tasks. prefix)
        original_data = {}
        for key, value in task.items():
            if key.startswith("tasks.") and not key.startswith("tasks.status"):
                original_key = key.replace("tasks.", "", 1)
                original_data[original_key] = value
        if original_data:
            return original_data
    return None


def extract_failed_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts failed tasks from task list.

    Args:
        tasks: List of tasks from report

    Returns:
        List of failed tasks in original format
    """
    failed_tasks = []

    for task in tasks:
        # For JSON/YAML reports, check status field
        if isinstance(task, dict):
            # Check JSON/YAML report format
            if "status" in task:
                extracted_task = _extract_from_json_yaml_report(task)
                if extracted_task:
                    failed_tasks.append(extracted_task)
            # For CSV/Excel reports, check field with tasks.status prefix
            elif "tasks.status" in task:
                extracted_task = _extract_from_csv_excel_report(task)
                if extracted_task:
                    failed_tasks.append(extracted_task)

    return failed_tasks


# Export internal functions for tests
__all__ = [
    "load_json_report",
    "load_yaml_report",
    "extract_failed_tasks",
    "_extract_from_json_yaml_report",
    "_extract_from_csv_excel_report",
]
