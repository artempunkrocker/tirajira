"""
Тесты для фабрики писателей отчетов.
"""

import pytest

from tirajira.report_writers.csv_writer import CsvReportWriter
from tirajira.report_writers.excel_writer import ExcelReportWriter
from tirajira.report_writers.factory import create_report_writer
from tirajira.report_writers.json_writer import JsonReportWriter
from tirajira.report_writers.xml_writer import XmlReportWriter
from tirajira.report_writers.yaml_writer import YamlReportWriter


def test_create_report_writer_json():
    """Тест: создание писателя отчетов для формата JSON"""
    # Создаем писатель отчетов
    writer = create_report_writer("json")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, JsonReportWriter)


def test_create_report_writer_yaml():
    """Тест: создание писателя отчетов для формата YAML"""
    # Создаем писатель отчетов
    writer = create_report_writer("yaml")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, YamlReportWriter)


def test_create_report_writer_yml():
    """Тест: создание писателя отчетов для формата YML"""
    # Создаем писатель отчетов
    writer = create_report_writer("yml")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, YamlReportWriter)


def test_create_report_writer_csv():
    """Тест: создание писателя отчетов для формата CSV"""
    # Создаем писатель отчетов
    writer = create_report_writer("csv")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, CsvReportWriter)


def test_create_report_writer_excel():
    """Тест: создание писателя отчетов для формата Excel"""
    # Создаем писатель отчетов
    writer = create_report_writer("excel")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, ExcelReportWriter)


def test_create_report_writer_xlsx():
    """Тест: создание писателя отчетов для формата XLSX"""
    # Создаем писатель отчетов
    writer = create_report_writer("xlsx")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, ExcelReportWriter)


def test_create_report_writer_xml():
    """Тест: создание писателя отчетов для формата XML"""
    # Создаем писатель отчетов
    writer = create_report_writer("xml")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, XmlReportWriter)


def test_create_report_writer_invalid_format():
    """Тест: создание писателя отчетов для неподдерживаемого формата"""
    # Проверяем, что выбрасывается исключение для неподдерживаемого формата
    with pytest.raises(ValueError, match="Не поддерживаемый формат отчета: txt"):
        create_report_writer("txt")


def test_create_report_writer_default():
    """Тест: создание писателя отчетов по умолчанию"""
    # Создаем писатель отчетов без указания формата
    writer = create_report_writer()

    # Проверяем, что создан писатель по умолчанию (JSON)
    assert isinstance(writer, JsonReportWriter)


def test_create_report_writer_case_insensitive():
    """Тест: создание писателя отчетов регистронезависимо"""
    # Создаем писатель отчетов в верхнем регистре
    writer = create_report_writer("JSON")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, JsonReportWriter)
