"""
YAML report writer.
"""

from typing import Any, Dict

import yaml

from .base import ReportWriter


class YamlReportWriter(ReportWriter):
    """YAML report writer."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Writes a report to a YAML file.

        Args:
            report_data: Report data to write
            file_path: Path to the report file
        """
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(report_data, f, allow_unicode=True, indent=2, sort_keys=False)
