"""
Фабрика для создания писателей отчетов.
"""

from typing import Dict, Type

from .base import ReportWriter
from .csv_writer import CsvReportWriter
from .excel_writer import ExcelReportWriter
from .json_writer import JsonReportWriter
from .xml_writer import XmlReportWriter
from .yaml_writer import YamlReportWriter


def create_report_writer(format: str = "json") -> ReportWriter:
    """
    Создает писатель отчетов в зависимости от формата.

    Args:
        format: Формат отчета (по умолчанию "json")

    Returns:
        ReportWriter: Писатель отчетов

    Raises:
        ValueError: Если формат не поддерживается
    """
    writers: Dict[str, Type[ReportWriter]] = {
        "json": JsonReportWriter,
        "yaml": YamlReportWriter,
        "yml": YamlReportWriter,
        "csv": CsvReportWriter,
        "xlsx": ExcelReportWriter,
        "excel": ExcelReportWriter,
        "xml": XmlReportWriter,
    }

    writer_class = writers.get(format.lower())
    if writer_class is None:
        raise ValueError(f"Не поддерживаемый формат отчета: {format}")

    return writer_class()
