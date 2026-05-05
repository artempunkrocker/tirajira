"""
JSON report writer.
"""

import json
from typing import Any, Dict

from .base import ReportWriter


class JsonReportWriter(ReportWriter):
    """JSON report writer."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Writes a report to a JSON file.

        Args:
            report_data: Report data to write
            file_path: Path to the report file
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
