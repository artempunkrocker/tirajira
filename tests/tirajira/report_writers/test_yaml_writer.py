"""
Тесты для писателя отчетов в формате YAML.
"""

from unittest.mock import mock_open, patch

from tirajira.report_writers.factory import create_report_writer
from tirajira.report_writers.yaml_writer import YamlReportWriter


@patch("builtins.open", new_callable=mock_open)
def test_yaml_report_writer_write_report(mock_file):
    """Тест: запись отчета в формате YAML"""
    # Создаем писатель отчетов
    writer = YamlReportWriter()

    # Создаем данные отчета
    report_data = {
        "metadata": {
            "generated_at": "2023-12-01T15:30:45",
            "source_file": "test.json",
            "total_tasks": 2,
            "successful_tasks": 1,
            "failed_tasks": 1,
        },
        "tasks": [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test task"},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "failure",
                "error_message": "Connection error",
                "issue_data": {"summary": "Another task"},
                "processed_at": "2023-12-01T15:30:46",
            },
        ],
    }

    # Записываем отчет
    writer.write_report(report_data, "report.yaml")

    # Проверяем, что файл открывался для записи
    mock_file.assert_called_once_with("report.yaml", "w", encoding="utf-8")


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
