"""
Писатель отчетов в формате YAML.
"""

from typing import Any, Dict

import yaml

from .base import ReportWriter


class YamlReportWriter(ReportWriter):
    """Писатель отчетов в формате YAML."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Записывает отчет в YAML файл.

        Args:
            report_data: Данные отчета для записи
            file_path: Путь к файлу отчета
        """
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(report_data, f, allow_unicode=True, indent=2, sort_keys=False)
