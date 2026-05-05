"""
Base class for report writers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ReportWriter(ABC):
    """Abstract class for writing reports."""

    @abstractmethod
    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Writes a report to a file.

        Args:
            report_data: Report data to write
            file_path: Path to the report file
        """
        pass
