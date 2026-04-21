#!/usr/bin/env python3
"""
Интеграционный тест для проверки работы режима --stop-on-error
"""

from unittest.mock import Mock, patch

from tirajira.main import create_tasks_from_file


@patch("tirajira.main.JiraClient")
@patch("tirajira.main.BatchProcessor")
def test_stop_on_error_integration(mock_batch_processor, mock_jira_client):
    """Интеграционный тест для проверки режима --stop-on-error"""
    print("Запуск интеграционного теста для --stop-on-error...")

    # Создаем тестовые данные
    test_file = "sample_tasks.json"

    # Мокаем TaskCreator
    with patch("tirajira.main.TaskCreator") as mock_task_creator:
        # Настраиваем моки
        mock_task_creator_instance = Mock()
        mock_task_creator_instance.create_from_file.return_value = (
            2  # Предположим, что 2 задачи созданы успешно
        )
        mock_task_creator.return_value = mock_task_creator_instance

        # Вызываем функцию с stop_on_error=True
        create_tasks_from_file(test_file, stop_on_error=True)

        # Проверяем, что TaskCreator был создан
        mock_task_creator.assert_called_once()
        # Проверяем, что метод create_from_file был вызван с правильными параметрами
        mock_task_creator_instance.create_from_file.assert_called_once_with(
            file_path=test_file,
            batch_size=10,
            delay=1.0,
            stop_on_error=True,
            verbose=False,
            report_file=None,
        )

        print("✅ Интеграционный тест прошел успешно!")
        print("✅ Режим --stop-on-error корректно передается в TaskCreator")


if __name__ == "__main__":
    test_stop_on_error_integration()
