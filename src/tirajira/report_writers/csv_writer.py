"""
CSV report writer.
"""

import csv
import json
from typing import Any, Dict

from ..logger import get_logger
from ..utils.flatten_utils import ListHandlingStrategy, flatten_dict
from .base import ReportWriter


class CsvReportWriter(ReportWriter):
    """CSV report writer."""

    def __init__(self) -> None:
        """Initializes the CSV report writer."""
        self.logger = get_logger()

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Writes a report to a CSV file.

        Args:
            report_data: Report data to write
            file_path: Path to the report file
        """
        try:
            # Convert nested structures to flat
            flattened_data = flatten_dict(
                report_data, list_handling=ListHandlingStrategy.INDEXED_EXPANSION
            )

            # Convert all values to strings for CSV
            csv_data = {}
            for key, value in flattened_data.items():
                if isinstance(value, (dict, list)):
                    # Convert complex objects to JSON strings
                    csv_data[key] = json.dumps(value, ensure_ascii=False)
                else:
                    csv_data[key] = str(value) if value is not None else ""

            # Write to CSV file
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write headers
                writer.writerow(csv_data.keys())
                # Write values
                writer.writerow(csv_data.values())
        except Exception as e:
            self.logger.error(f"Error writing CSV report to file {file_path}: {str(e)}")
            raise
