"""
Тесты для писателя отчетов в формате CSV.
"""

from unittest.mock import mock_open, patch

from tirajira.report_writers.csv_writer import CsvReportWriter
from tirajira.report_writers.factory import create_report_writer


@patch("builtins.open", new_callable=mock_open)
def test_csv_report_writer_write_report(mock_file):
    """Тест: запись отчета в формате CSV"""
    # Создаем писатель отчетов
    writer = CsvReportWriter()

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
    writer.write_report(report_data, "report.csv")

    # Проверяем, что файл открывался для записи
    mock_file.assert_called_once_with("report.csv", "w", newline="", encoding="utf-8")


def test_create_report_writer_csv():
    """Тест: создание писателя отчетов для формата CSV"""
    # Создаем писатель отчетов
    writer = create_report_writer("csv")

    # Проверяем, что создан правильный тип писателя
    assert isinstance(writer, CsvReportWriter)
