"""
Писатель отчетов в формате JSON.
"""

import json
from typing import Any, Dict

from .base import ReportWriter


class JsonReportWriter(ReportWriter):
    """Писатель отчетов в формате JSON."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Записывает отчет в JSON файл.

        Args:
            report_data: Данные отчета для записи
            file_path: Путь к файлу отчета
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
