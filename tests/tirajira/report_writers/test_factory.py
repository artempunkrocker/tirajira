"""
Tests for the report writers factory.
"""

import pytest

from tirajira.report_writers.csv_writer import CsvReportWriter
from tirajira.report_writers.excel_writer import ExcelReportWriter
from tirajira.report_writers.factory import create_report_writer
from tirajira.report_writers.json_writer import JsonReportWriter
from tirajira.report_writers.xml_writer import XmlReportWriter
from tirajira.report_writers.yaml_writer import YamlReportWriter


def test_create_report_writer_json():
    """Test: creating a report writer for JSON format"""
    # Create a report writer
    writer = create_report_writer("json")

    # Check that the correct type of writer was created
    assert isinstance(writer, JsonReportWriter)


def test_create_report_writer_yaml():
    """Test: creating a report writer for YAML format"""
    # Create a report writer
    writer = create_report_writer("yaml")

    # Check that the correct type of writer was created
    assert isinstance(writer, YamlReportWriter)


def test_create_report_writer_yml():
    """Test: creating a report writer for YML format"""
    # Create a report writer
    writer = create_report_writer("yml")

    # Check that the correct type of writer was created
    assert isinstance(writer, YamlReportWriter)


def test_create_report_writer_csv():
    """Test: creating a report writer for CSV format"""
    # Create a report writer
    writer = create_report_writer("csv")

    # Check that the correct type of writer was created
    assert isinstance(writer, CsvReportWriter)


def test_create_report_writer_excel():
    """Test: creating a report writer for Excel format"""
    # Create a report writer
    writer = create_report_writer("excel")

    # Check that the correct type of writer was created
    assert isinstance(writer, ExcelReportWriter)


def test_create_report_writer_xlsx():
    """Test: creating a report writer for XLSX format"""
    # Create a report writer
    writer = create_report_writer("xlsx")

    # Check that the correct type of writer was created
    assert isinstance(writer, ExcelReportWriter)


def test_create_report_writer_xml():
    """Test: creating a report writer for XML format"""
    # Create a report writer
    writer = create_report_writer("xml")

    # Check that the correct type of writer was created
    assert isinstance(writer, XmlReportWriter)


def test_create_report_writer_invalid_format():
    """Test: creating a report writer for unsupported format"""
    # Check that an exception is thrown for unsupported format
    with pytest.raises(ValueError, match="Unsupported report format: txt"):
        create_report_writer("txt")


def test_create_report_writer_default():
    """Test: creating a default report writer"""
    # Create a report writer without specifying a format
    writer = create_report_writer()

    # Check that the default writer (JSON) was created
    assert isinstance(writer, JsonReportWriter)


def test_create_report_writer_case_insensitive():
    """Test: creating a report writer case-insensitively"""
    # Create a report writer in uppercase
    writer = create_report_writer("JSON")

    # Check that the correct type of writer was created
    assert isinstance(writer, JsonReportWriter)
