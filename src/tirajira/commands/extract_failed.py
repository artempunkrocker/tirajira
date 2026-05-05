"""
Command to extract failed tasks from a report.
"""

import os
from typing import Any, Dict, List, Optional

from ..file_loaders import create_file_loader
from ..report_writers.factory import create_report_writer
from ..utils.path_validation import validate_file_path
from .base import BaseCommand
from .exception_handler import handle_exceptions
from .utils import (
    _extract_from_csv_excel_report,
    _extract_from_json_yaml_report,
    extract_failed_tasks,
    load_json_report,
    load_yaml_report,
)


class ExtractFailedCommand(BaseCommand):
    """Command to extract failed tasks from a report."""

    @handle_exceptions
    def execute(self):
        """Executes extracting failed tasks from a report."""
        # Check existence of report file with safe path validation
        try:
            validate_file_path(self.args.report_file)
        except (ValueError, FileNotFoundError) as e:
            self.logger.error(
                f"Report file {self.args.report_file} not found "
                f"or path is unsafe: {str(e)}"
            )
            return 1

        # Determine report file type by extension
        _, file_extension = os.path.splitext(self.args.report_file)

        # For JSON and YAML report files, use special logic
        if file_extension.lower() in [".json"]:
            report_data = load_json_report(self.args.report_file)
            tasks = report_data.get("tasks", [])
        elif file_extension.lower() in [".yaml", ".yml"]:
            report_data = load_yaml_report(self.args.report_file)
            tasks = report_data.get("tasks", [])
        # For other formats, use existing approach
        else:
            # Create appropriate file loader
            loader = create_file_loader(file_extension)

            # Load data from report
            report_data = loader.load_issues(self.args.report_file)

            # If this is a CSV/Excel report, then it's a list of tasks with prefixes
            tasks = report_data

        # Extract failed tasks
        failed_tasks = extract_failed_tasks(tasks)

        # Check if there are failed tasks
        if not failed_tasks:
            self.logger.info("No failed tasks found in report")
            return 0

        self.logger.info(f"Found {len(failed_tasks)} failed tasks")

        # Determine output file format by extension
        _, output_extension = os.path.splitext(self.args.output_file)
        output_format = output_extension[1:].lower() if output_extension else "json"

        # If extension is not supported, use JSON
        if output_format not in ["json", "yaml", "yml", "csv", "xlsx", "excel"]:
            output_format = "json"

        # If user specified filename without extension, add .json
        if not output_extension:
            self.args.output_file += ".json"

        # Create report writer and write extracted tasks
        writer = create_report_writer(output_format)

        # For JSON/YAML formats, save as list of tasks
        # For CSV/Excel formats, also save as list of tasks
        writer.write_report(failed_tasks, self.args.output_file)

        self.logger.success(f"Extracted tasks saved to file: {self.args.output_file}")

        return 0

    def run(self):
        """
        Template method for executing the command.
        """
        verbose = getattr(self.args, "verbose", False)
        self.logger.set_verbose(verbose)
        return self.execute()

    def _load_report(self, file_path: str) -> Dict[str, Any]:
        _, file_extension = os.path.splitext(file_path)

        if file_extension.lower() in [".json"]:
            return load_json_report(file_path)
        elif file_extension.lower() in [".yaml", ".yml"]:
            return load_yaml_report(file_path)
        else:
            raise ValueError(f"Unsupported report file format: {file_extension}")

    def _load_json_report(self, file_path: str) -> Dict[str, Any]:
        return load_json_report(file_path)

    def _load_yaml_report(self, file_path: str) -> Dict[str, Any]:
        return load_yaml_report(file_path)

    def _extract_from_json_yaml_report(
        self, task: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return _extract_from_json_yaml_report(task)

    def _extract_from_csv_excel_report(
        self, task: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return _extract_from_csv_excel_report(task)

    def _extract_failed_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return extract_failed_tasks(tasks)
