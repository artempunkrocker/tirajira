"""
Тесты для TaskCreator с функциональностью отчетов.
"""

import os
from unittest.mock import Mock, mock_open, patch

from tirajira.task_creator import TaskCreator


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
@patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
def test_task_creator_create_from_file_with_report_auto_name(
    mock_file, mock_batch_processor, mock_jira_client, mock_create_file_loader
):
    """Тест: создание задач из файла с автоматическим именем отчета"""
    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]
    mock_create_file_loader.return_value = mock_loader

    # Настраиваем mock для batch processor
    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (
        2,  # successful_count
        [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "success",
                "issue_key": "PROJ-124",
                "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:46",
            },
        ],
    )
    mock_batch_processor.return_value = mock_batch_processor_instance

    # Создаем TaskCreator
    task_creator = TaskCreator()

    with patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
        # Вызываем метод с автоматическим именем отчета
        result = task_creator.create_from_file(file_path="test.json", report_file=True)

        # Проверяем результат
        assert result == 2

        # Проверяем, что методы были вызваны правильно
        mock_create_file_loader.assert_called_once()
        mock_loader.load_issues.assert_called_once_with("test.json")
        mock_batch_processor_instance.process.assert_called_once()


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
@patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
@patch("os.path.exists")
def test_task_creator_create_from_file_with_report_custom_name(
    mock_exists,
    mock_file,
    mock_batch_processor,
    mock_jira_client,
    mock_create_file_loader,
):
    """Тест: создание задач из файла с указанным именем отчета"""
    # Настраиваем mock для проверки существования файла
    mock_exists.return_value = True

    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]
    mock_create_file_loader.return_value = mock_loader

    # Настраиваем mock для batch processor
    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (
        1,  # successful_count
        [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "failure",
                "error_message": "Connection error",
                "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:46",
            },
        ],
    )
    mock_batch_processor.return_value = mock_batch_processor_instance

    # Создаем TaskCreator
    task_creator = TaskCreator()

    with patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
        # Вызываем метод с указанным именем отчета
        result = task_creator.create_from_file(
            file_path="test.json", report_file="report.json"
        )

        # Проверяем результат
        assert result == 1

        # Проверяем, что методы были вызваны правильно
        mock_create_file_loader.assert_called_once()
        mock_loader.load_issues.assert_called_once_with("test.json")
        mock_batch_processor_instance.process.assert_called_once()


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
@patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
@patch("os.path.exists")
def test_task_creator_create_from_file_with_csv_report(
    mock_exists,
    mock_file,
    mock_batch_processor,
    mock_jira_client,
    mock_create_file_loader,
):
    """Тест: создание задач из файла с сохранением отчета в формате CSV"""
    # Настраиваем mock для проверки существования файла
    mock_exists.return_value = True

    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]
    mock_create_file_loader.return_value = mock_loader

    # Настраиваем mock для batch processor
    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (
        2,  # successful_count
        [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "success",
                "issue_key": "PROJ-124",
                "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:46",
            },
        ],
    )
    mock_batch_processor.return_value = mock_batch_processor_instance

    # Создаем TaskCreator
    task_creator = TaskCreator()

    with patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
        # Вызываем метод с именем отчета в формате CSV
        result = task_creator.create_from_file(
            file_path="test.json", report_file="report.csv"
        )

        # Проверяем результат
        assert result == 2

        # Проверяем, что методы были вызваны правильно
        mock_create_file_loader.assert_called_once()
        mock_loader.load_issues.assert_called_once_with("test.json")
        mock_batch_processor_instance.process.assert_called_once()


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
@patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
@patch("os.path.exists")
def test_task_creator_create_from_file_without_report(
    mock_exists,
    mock_file,
    mock_batch_processor,
    mock_jira_client,
    mock_create_file_loader,
):
    """Тест: создание задач из файла без сохранения отчета"""
    # Настраиваем mock для проверки существования файла
    mock_exists.return_value = True

    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]
    mock_create_file_loader.return_value = mock_loader

    # Настраиваем mock для batch processor
    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (
        2,  # successful_count
        [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "success",
                "issue_key": "PROJ-124",
                "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:46",
            },
        ],
    )
    mock_batch_processor.return_value = mock_batch_processor_instance

    # Создаем TaskCreator
    task_creator = TaskCreator()

    # Вызываем метод без сохранения отчета
    result = task_creator.create_from_file(file_path="test.json", report_file=None)

    # Проверяем результат
    assert result == 2

    # Проверяем, что методы были вызваны правильно
    mock_create_file_loader.assert_called_once()
    mock_loader.load_issues.assert_called_once_with("test.json")
    mock_batch_processor_instance.process.assert_called_once()


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
@patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
@patch("os.path.exists")
def test_task_creator_create_from_file_with_unsupported_extension(
    mock_exists,
    mock_file,
    mock_batch_processor,
    mock_jira_client,
    mock_create_file_loader,
):
    """Тест: создание задач из файла с нестандартным расширением
    (должно сохраняться как JSON)"""
    # Настраиваем mock для проверки существования файла
    mock_exists.return_value = True

    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]
    mock_create_file_loader.return_value = mock_loader

    # Настраиваем mock для batch processor
    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (
        2,  # successful_count
        [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "success",
                "issue_key": "PROJ-124",
                "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:46",
            },
        ],
    )
    mock_batch_processor.return_value = mock_batch_processor_instance

    # Создаем TaskCreator
    task_creator = TaskCreator()

    with patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
        # Вызываем метод с нестандартным расширением
        result = task_creator.create_from_file(
            file_path="test.json", report_file="report.xml"
        )

        # Проверяем результат
        assert result == 2

        # Проверяем, что методы были вызваны правильно
        mock_create_file_loader.assert_called_once()
        mock_loader.load_issues.assert_called_once_with("test.json")
        mock_batch_processor_instance.process.assert_called_once()


def test_task_creator_save_report_json():
    """Тест: сохранение отчета в формате JSON."""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "failure",
            "error_message": "Connection error",
            "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:46",
        },
    ]

    # Мокаем open для записи отчета
    with patch("builtins.open", mock_open()) as mock_file:
        # Вызываем метод сохранения отчета
        task_creator._save_report("tasks.json", processing_details, "report.json", 1, 2)

        # Проверяем, что файл был открыт для записи
        mock_file.assert_called_once_with("report.json", "w", encoding="utf-8")


def test_task_creator_save_report_csv():
    """Тест: сохранение отчета в формате CSV."""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "failure",
            "error_message": "Connection error",
            "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:46",
        },
    ]

    # Мокаем create_report_writer
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer:
        mock_create_report_writer.return_value = mock_report_writer

        # Мокаем open
        with patch("builtins.open", mock_open()):
            # Вызываем метод сохранения отчета
            task_creator._save_report(
                "tasks.csv", processing_details, "report.csv", 1, 2
            )

            # Проверяем, что create_report_writer был вызван с правильным аргументом
            mock_create_report_writer.assert_called_once_with("csv")
            mock_report_writer.write_report.assert_called_once()


def test_task_creator_save_report_yaml():
    """Тест: сохранение отчета в формате YAML."""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "failure",
            "error_message": "Connection error",
            "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:46",
        },
    ]

    # Мокаем create_report_writer
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer:
        mock_create_report_writer.return_value = mock_report_writer

        # Мокаем open
        with patch("builtins.open", mock_open()):
            # Вызываем метод сохранения отчета
            task_creator._save_report(
                "tasks.yaml", processing_details, "report.yaml", 1, 2
            )

            # Проверяем, что create_report_writer был вызван с правильным аргументом
            mock_create_report_writer.assert_called_once_with("yaml")
            mock_report_writer.write_report.assert_called_once()


def test_task_creator_save_report_excel():
    """Тест: сохранение отчета в формате Excel."""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "failure",
            "error_message": "Connection error",
            "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:46",
        },
    ]

    # Мокаем create_report_writer
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer:
        mock_create_report_writer.return_value = mock_report_writer

        # Мокаем open
        with patch("builtins.open", mock_open()):
            # Вызываем метод сохранения отчета
            task_creator._save_report(
                "tasks.xlsx", processing_details, "report.xlsx", 1, 2
            )

            # Проверяем, что create_report_writer был вызван с правильным аргументом
            mock_create_report_writer.assert_called_once_with("xlsx")
            mock_report_writer.write_report.assert_called_once()


def test_task_creator_save_report_unsupported_format():
    """Тест: сохранение отчета в неподдерживаемом формате
    (должно сохраняться как JSON)."""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "failure",
            "error_message": "Connection error",
            "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:46",
        },
    ]

    # Мокаем create_report_writer
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer:
        mock_create_report_writer.return_value = mock_report_writer

        # Мокаем open
        with patch("builtins.open", mock_open()):
            # Вызываем метод сохранения отчета
            task_creator._save_report(
                "tasks.txt", processing_details, "report.txt", 1, 1
            )

            # Проверяем, что create_report_writer был вызван с форматом JSON
            mock_create_report_writer.assert_called_once_with("json")
            mock_report_writer.write_report.assert_called_once()


def test_task_creator_update_batch_processor_logger():
    """Тест: обновление логгера в batch_processor (строки 72->75)"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_logger = Mock()

    # Настраиваем mock для logger
    with patch("tirajira.task_creator.get_logger") as mock_get_logger:
        mock_get_logger.return_value = mock_logger

        # Создаем создателя задач
        task_creator = TaskCreator(
            jira_client=mock_jira_client,
            batch_processor=mock_batch_processor,
            verbose=False,
        )

        # Проверяем, что метод set_verbose был вызван у логгера TaskCreator
        task_creator.logger.set_verbose.assert_called_with(False)


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
def test_task_creator_create_from_file_exception_handling(
    mock_batch_processor, mock_jira_client, mock_create_file_loader
):
    """Тест: обработка исключений в create_from_file (строки 111-113)"""
    # Настраиваем mock для загрузчика файлов, чтобы он выбрасывал исключение
    mock_create_file_loader.side_effect = Exception("Ошибка загрузки файла")

    # Создаем TaskCreator
    task_creator = TaskCreator()

    # Проверяем, что при возникновении исключения вызывается sys.exit(1)
    with patch("sys.exit") as mock_exit:
        task_creator.create_from_file("test.json")
        mock_exit.assert_called_once_with(1)


@patch("tirajira.task_creator.create_file_loader")
@patch("tirajira.task_creator.JiraClient")
@patch("tirajira.task_creator.BatchProcessor")
@patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
def test_task_creator_create_from_file_no_report_saved(
    mock_file, mock_batch_processor, mock_jira_client, mock_create_file_loader
):
    """Тест: возврат без сохранения отчета (строка 139)"""
    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
    ]
    mock_create_file_loader.return_value = mock_loader

    # Настраиваем mock для batch processor
    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (1, [])
    mock_batch_processor.return_value = mock_batch_processor_instance

    # Создаем TaskCreator
    task_creator = TaskCreator()

    # Вызываем метод без сохранения отчета (report_file=None)
    result = task_creator.create_from_file("test.json", report_file=None)

    # Проверяем результат
    assert result == 1


def test_task_creator_save_report_issue_urls():
    """Тест: генерация URL задач (строки 150, 158-159)"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        }
    ]

    # Мокаем create_report_writer и open
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer, patch("builtins.open", mock_open()), patch.dict(
        os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}
    ):
        mock_create_report_writer.return_value = mock_report_writer

        # Вызываем метод сохранения отчета
        task_creator._save_report("tasks.json", processing_details, "report.json", 1, 1)

        # Проверяем, что в processing_details добавлен issue_url
        assert "issue_url" in processing_details[0]
        assert (
            processing_details[0]["issue_url"]
            == "https://test.atlassian.net/browse/PROJ-123"
        )


def test_task_creator_save_report_exception_handling():
    """Тест: обработка исключений при сохранении отчета (строки 179-180)"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        }
    ]

    # Мокаем create_report_writer, чтобы он выбрасывал исключение
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer:
        mock_create_report_writer.side_effect = Exception("Ошибка сохранения отчета")

        # Мокаем open
        with patch("builtins.open", mock_open()):
            # Проверяем, что исключение обрабатывается и не прерывает выполнение
            with patch.object(task_creator.logger, "error") as mock_error:
                task_creator._save_report(
                    "tasks.json", processing_details, "report.json", 1, 1
                )
                # Проверяем, что ошибка была залогирована
                mock_error.assert_called_once()
                assert "Ошибка при сохранении отчета" in mock_error.call_args[0][0]


def test_task_creator_save_report_issue_urls_generation():
    """Тест: проверка формирования URL задач в отчетах"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета с несколькими задачами
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "success",
            "issue_key": "PROJ-124",
            "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:46",
        },
        {
            "id": 2,
            "status": "failure",
            "error_message": "Connection error",
            "issue_key": "PROJ-125",  # Добавляем issue_key для третьей задачи
            "issue_data": {"summary": "Test 3", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:47",
        },
    ]

    # Мокаем create_report_writer и open
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer, patch("builtins.open", mock_open()), patch.dict(
        os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}
    ):
        mock_create_report_writer.return_value = mock_report_writer

        # Вызываем метод сохранения отчета
        task_creator._save_report("tasks.json", processing_details, "report.json", 2, 3)

        # Проверяем, что в processing_details добавлены issue_url
        # для всех задач с issue_key
        assert "issue_url" in processing_details[0]
        assert (
            processing_details[0]["issue_url"]
            == "https://test.atlassian.net/browse/PROJ-123"
        )
        assert "issue_url" in processing_details[1]
        assert (
            processing_details[1]["issue_url"]
            == "https://test.atlassian.net/browse/PROJ-124"
        )
        # Для неуспешных задач URL тоже должен быть добавлен, если есть issue_key
        assert "issue_url" in processing_details[2]
        assert (
            processing_details[2]["issue_url"]
            == "https://test.atlassian.net/browse/PROJ-125"
        )


def test_task_creator_save_report_auto_filename_generation():
    """Тест: проверка автоматической генерации имен файлов отчетов"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        }
    ]

    # Мокаем create_report_writer, datetime и open
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer, patch(
        "tirajira.task_creator.datetime"
    ) as mock_datetime, patch("builtins.open", mock_open()):
        mock_create_report_writer.return_value = mock_report_writer
        mock_datetime.now.return_value.strftime.return_value = "20231201_153045"

        # Вызываем метод сохранения отчета с автоматической генерацией имени
        task_creator._save_report("tasks.json", processing_details, True, 1, 1)

        # Проверяем, что имя файла было сгенерировано правильно
        expected_filename = "tirajira_report_20231201_153045.json"
        mock_report_writer.write_report.assert_called_once()
        call_args = mock_report_writer.write_report.call_args[0]
        assert call_args[1] == expected_filename


def test_task_creator_save_report_different_formats():
    """Тест: проверка работы с различными форматами отчетов"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        }
    ]

    test_cases = [
        ("report.json", "json"),
        ("report.yaml", "yaml"),
        ("report.yml", "yml"),
        ("report.csv", "csv"),
        ("report.xlsx", "xlsx"),
        ("report.excel", "excel"),
    ]

    for filename, expected_format in test_cases:
        with patch(
            "tirajira.task_creator.create_report_writer"
        ) as mock_create_report_writer, patch("builtins.open", mock_open()):
            # Вызываем метод сохранения отчета
            task_creator._save_report("tasks.json", processing_details, filename, 1, 1)

            # Проверяем, что create_report_writer был вызван с правильным форматом
            mock_create_report_writer.assert_called_with(expected_format)


def test_task_creator_save_report_no_extension_adds_json():
    """Тест: проверка добавления расширия .json если оно не указано"""
    # Создаем mocks
    mock_jira_client = Mock()
    mock_batch_processor = Mock()
    mock_report_writer = Mock()

    # Создаем создателя задач
    task_creator = TaskCreator(
        jira_client=mock_jira_client,
        batch_processor=mock_batch_processor,
        verbose=False,
    )

    # Данные для отчета
    processing_details = [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
            "processed_at": "2023-12-01T15:30:45",
        }
    ]

    # Мокаем create_report_writer
    with patch(
        "tirajira.task_creator.create_report_writer"
    ) as mock_create_report_writer:
        mock_create_report_writer.return_value = mock_report_writer

        # Тестируем случай, когда расширение не поддерживается
        # В этом случае должно использоваться расширение .json
        with patch("builtins.open", mock_open()):
            task_creator._save_report(
                "tasks.json", processing_details, "report.xml", 1, 1
            )
            # Проверяем, что файл был сохранен с расширением .xml
            # (поддерживаемый формат)
            mock_report_writer.write_report.assert_called_once()
            call_args = mock_report_writer.write_report.call_args[0]
            assert call_args[1] == "report.xml"

        # Сбросим mock для следующего теста
        mock_report_writer.reset_mock()

        # Тестируем случай, когда формат не определен
        # В этом случае должно использоваться расширение .json
        with patch("builtins.open", mock_open()):
            task_creator._save_report(
                "tasks.json",
                processing_details,
                "report_without_known_extension.xyz",
                1,
                1,
            )
            # При неподдерживаемом формате используется JSON
            mock_report_writer.write_report.assert_called_once()
            call_args = mock_report_writer.write_report.call_args[0]
            assert call_args[1] == "report_without_known_extension.xyz"
