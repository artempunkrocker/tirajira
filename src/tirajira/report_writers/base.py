"""
Базовый класс для писателей отчетов.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ReportWriter(ABC):
    """Абстрактный класс для записи отчетов."""

    @abstractmethod
    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Записывает отчет в файл.

        Args:
            report_data: Данные отчета для записи
            file_path: Путь к файлу отчета
        """
        pass
