"""
Module for generating reports on created issues.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..logger import get_logger
from ..report_writers.factory import create_report_writer


class ReportGenerator:
    """Class for generating operation execution reports."""

    def __init__(self) -> None:
        """Initializes the report generator."""
        self.logger = get_logger()

    def generate_report(
        self,
        source_file: str,
        processing_details: List[Dict[str, Any]],
        report_file: Optional[str],
        successful_count: int,
        total_count: int,
        jira_server: Optional[str] = None,
    ) -> None:
        """
        Generates a report on operation execution.

        Args:
            source_file: Path to the source file with issues.
            processing_details: Details of issue processing.
            report_file: Path to the report file (None - don't save report,
                        True - automatically generate filename,
                        str - use the specified filename).
            successful_count: Number of successfully created issues.
            total_count: Total number of issues.
            jira_server: Jira server URL (optional).
        """
        try:
            if report_file is True:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = f"tirajira_report_{timestamp}.json"
            elif isinstance(report_file, str):
                report_path = report_file
            else:
                return

            _, file_extension = os.path.splitext(report_path)
            report_format = file_extension[1:].lower() if file_extension else "json"

            supported_formats = ["json", "yaml", "yml", "csv", "xlsx", "excel", "xml"]
            if report_format not in supported_formats:
                report_format = "json"
                if isinstance(report_file, str) and not file_extension:
                    report_path += ".json"

            if jira_server is not None:
                for detail in processing_details:
                    if detail.get("issue_key"):
                        detail["issue_url"] = (
                            f"{jira_server.rstrip('/')}/browse/{detail['issue_key']}"
                        )

            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "source_file": source_file,
                    "jira_server": jira_server,
                    "total_tasks": total_count,
                    "successful_tasks": successful_count,
                    "failed_tasks": total_count - successful_count,
                },
                "tasks": processing_details,
            }

            writer = create_report_writer(report_format)
            writer.write_report(report_data, report_path)

            self.logger.info(f"Report saved to file: {report_path}")
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
