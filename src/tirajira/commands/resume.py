"""
Command to resume execution from a report.
"""

import json
import os
from typing import Any, Dict, List, Optional, TextIO

import yaml

from ..file_loaders import create_file_loader
from ..utils.path_validation import validate_file_path
from .base import BaseCommand
from .exception_handler import handle_exceptions
from .utils import (
    _extract_from_csv_excel_report,
    _extract_from_json_yaml_report,
    extract_failed_tasks,
)


class ResumeCommand(BaseCommand):
    """Command to resume execution from a report."""

    @handle_exceptions
    def execute(self):
        """Executes resuming execution from a report."""
        logger = self.logger
        logger.set_verbose(self.args.verbose)

        # Check existence of report file with safe path validation
        try:
            validate_file_path(self.args.report_file)
        except (ValueError, FileNotFoundError) as e:
            logger.error(
                f"Report file {self.args.report_file} not found "
                f"or path is unsafe: {str(e)}"
            )
            return 1

        # Determine report file type by extension
        _, file_extension = os.path.splitext(self.args.report_file)

        # For JSON and YAML report files, use special logic
        if file_extension.lower() in [".json"]:
            report_data = self._load_json_report(self.args.report_file)
            tasks = report_data.get("tasks", [])
            source_file = report_data.get("metadata", {}).get("source_file", "")
        elif file_extension.lower() in [".yaml", ".yml"]:
            report_data = self._load_yaml_report(self.args.report_file)
            tasks = report_data.get("tasks", [])
            source_file = report_data.get("metadata", {}).get("source_file", "")
        # For other formats, use existing approach
        else:
            # Create appropriate file loader
            loader = create_file_loader(file_extension)

            # Load data from report
            report_data = loader.load_issues(self.args.report_file)

            # If this is a CSV/Excel report, then it's a list of tasks with prefixes
            tasks = report_data
            # For CSV/Excel reports we cannot get source_file,
            # so we use the report path as the source
            source_file = self.args.report_file

        # Extract failed tasks
        failed_tasks = self._extract_failed_tasks(tasks)

        # Check if there are failed tasks
        if not failed_tasks:
            logger.info("No failed tasks found in report for reprocessing")
            return 0

        logger.info(f"Found {len(failed_tasks)} failed tasks for reprocessing")

        # Batch sending of failed tasks
        successful_count, processing_details = self.rate_limiter.process(
            failed_tasks,
            max_concurrent_requests=self.args.max_concurrent_requests,
            min_request_interval=self.args.min_request_interval,
            stop_on_error=self.args.stop_on_error,
            verbose=self.args.verbose,
        )

        logger.success(
            f"Successfully processed {successful_count} of {len(failed_tasks)} tasks"
        )

        # Save report if required
        if self.args.report is not None:
            # Use source_file from report metadata for logging
            self.task_creator._save_report(
                source_file,
                processing_details,
                self.args.report,
                successful_count,
                len(failed_tasks),
            )

        return 0

    def _load_report(self, file_path: str) -> Dict[str, Any]:
        """
        Loads report from file.

        Args:
            file_path: Path to report file

        Returns:
            Dictionary with report data
        """
        _, file_extension = os.path.splitext(file_path)

        if file_extension.lower() in [".json"]:
            return self._load_json_report(file_path)
        elif file_extension.lower() in [".yaml", ".yml"]:
            return self._load_yaml_report(file_path)
        else:
            raise ValueError(f"Unsupported report file format: {file_extension}")

    def _load_json_report(
        self, file_path: str, file_handler: Optional[TextIO] = None
    ) -> Dict[str, Any]:
        """
        Loads report from JSON file.

        Args:
            file_path: Path to JSON report file
            file_handler: Optional file descriptor

        Returns:
            Dictionary with report data
        """
        try:
            if file_handler is not None:
                report_data = json.load(file_handler)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)

            if not isinstance(report_data, dict):
                raise ValueError("JSON report file must contain an object")

            return report_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON report file: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Error reading report file: {str(e)}") from e

    def _load_yaml_report(
        self, file_path: str, file_handler: Optional[TextIO] = None
    ) -> Dict[str, Any]:
        """
        Loads report from YAML file.

        Args:
            file_path: Path to YAML report file
            file_handler: Optional file descriptor

        Returns:
            Dictionary with report data
        """
        try:
            if file_handler is not None:
                report_data = yaml.safe_load(file_handler)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    report_data = yaml.safe_load(f)

            if not isinstance(report_data, dict):
                raise ValueError("YAML report file must contain an object")

            return report_data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML report file: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Error reading report file: {str(e)}") from e

    def _extract_from_json_yaml_report(
        self, task: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extracts task from JSON/YAML report."""
        return _extract_from_json_yaml_report(task)

    def _extract_from_csv_excel_report(
        self, task: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extracts task from CSV/Excel report."""
        return _extract_from_csv_excel_report(task)

    def _extract_failed_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extracts failed tasks from task list.

        Args:
            tasks: List of tasks from report

        Returns:
            List of failed tasks in original format
        """
        return extract_failed_tasks(tasks)
