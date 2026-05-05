"""
Factory for creating report writers.
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
    Creates a report writer depending on the format.

    Args:
        format: Report format (default "json")

    Returns:
        ReportWriter: Report writer

    Raises:
        ValueError: If format is not supported
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
        raise ValueError(f"Unsupported report format: {format}")

    return writer_class()
