"""
Тесты для писателя отчетов XML.
"""

import os
import tempfile
import xml.etree.ElementTree as ET

from tirajira.report_writers.xml_writer import XmlReportWriter


def test_xml_report_writer_write_report():
    """Тест: запись отчета в формате XML"""
    # Создаем писатель отчетов
    writer = XmlReportWriter()

    # Создаем данные отчета
    report_data = {
        "metadata": {
            "generated_at": "2023-12-01T15:30:45",
            "source_file": "test.xml",
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

    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    try:
        # Записываем отчет
        writer.write_report(report_data, tmp_file_path)

        # Проверяем, что файл был создан
        assert os.path.exists(tmp_file_path)

        # Проверяем содержимое файла
        tree = ET.parse(tmp_file_path)
        root = tree.getroot()

        # Проверяем корневой элемент
        assert root.tag == "report"

        # Проверяем наличие элементов metadata и tasks
        metadata_element = root.find("metadata")
        tasks_element = root.find("tasks")
        assert metadata_element is not None
        assert tasks_element is not None

        # Проверяем содержимое метаданных
        generated_at_element = metadata_element.find("generated_at")
        assert generated_at_element is not None
        assert generated_at_element.text == "2023-12-01T15:30:45"

        # Проверяем содержимое задач
        task_elements = tasks_element.findall("task")
        assert len(task_elements) == 2

        # Проверяем первую задачу
        first_task = task_elements[0]
        status_element = first_task.find("status")
        assert status_element is not None
        assert status_element.text == "success"

    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


def test_xml_report_writer_with_nested_data():
    """Тест: запись отчета с вложенными данными"""
    # Создаем писатель отчетов
    writer = XmlReportWriter()

    # Создаем данные отчета с вложенными структурами
    report_data = {
        "metadata": {
            "generated_at": "2023-12-01T15:30:45",
            "source_file": "nested_test.xml",
            "total_tasks": 1,
            "successful_tasks": 1,
            "failed_tasks": 0,
        },
        "tasks": [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-124",
                "issue_data": {
                    "summary": "Nested data task",
                    "description": "Task with nested data structures",
                    "assignee": {"name": "John Doe", "email": "john.doe@example.com"},
                    "custom_fields": {"business_value": "High", "story_points": 5},
                },
                "labels": ["urgent", "backend"],
                "processed_at": "2023-12-01T15:30:47",
            }
        ],
    }

    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    try:
        # Записываем отчет
        writer.write_report(report_data, tmp_file_path)

        # Проверяем, что файл был создан
        assert os.path.exists(tmp_file_path)

        # Проверяем содержимое файла
        tree = ET.parse(tmp_file_path)
        root = tree.getroot()

        # Проверяем корневой элемент
        assert root.tag == "report"

        # Проверяем наличие элементов metadata и tasks
        metadata_element = root.find("metadata")
        tasks_element = root.find("tasks")
        assert metadata_element is not None
        assert tasks_element is not None

        # Проверяем содержимое задачи
        task_elements = tasks_element.findall("task")
        assert len(task_elements) == 1

        # Проверяем вложенные данные
        task = task_elements[0]
        issue_data_element = task.find("issue_data")
        assert issue_data_element is not None

        assignee_element = issue_data_element.find("assignee")
        assert assignee_element is not None

        name_element = assignee_element.find("name")
        assert name_element is not None
        assert name_element.text == "John Doe"

    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
