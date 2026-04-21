"""
Тесты для команды возобновления выполнения TiraJira.
"""

from unittest.mock import Mock, mock_open, patch

import pytest

from tirajira.commands.resume import ResumeCommand


@patch("tirajira.commands.resume.os.path.exists")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_file_not_found(mock_get_logger, mock_exists):
    """Тест: обработка случая, когда файл отчета не найден"""
    # Настраиваем mock
    mock_exists.return_value = False
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "nonexistent.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 1

    # Проверяем, что логгер записал ошибку
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once_with("Файл отчета nonexistent.json не найден")


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open", new_callable=mock_open, read_data='{"tasks": []}'
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_no_failed_tasks(
    mock_get_logger, mock_json_load, mock_file, mock_exists
):
    """Тест: обработка случая, когда в отчете нет неудачных задач
    для повторной обработки"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {"tasks": []}
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with(
        "Не найдено неудачных задач в отчете для повторной обработки"
    )


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "success"}]}',
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.JiraClient")
@patch("tirajira.commands.resume.BatchProcessor")
@patch("tirajira.commands.resume.TaskCreator")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_no_failed_tasks_to_process(
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
    mock_json_load,
    mock_file,
    mock_exists,
):
    """Тест: обработка случая, когда в отчете есть задачи, но все успешные"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "success", "issue_data": {"summary": "Success task"}}]
    }
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with(
        "Не найдено неудачных задач в отчете для повторной обработки"
    )


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.JiraClient")
@patch("tirajira.commands.resume.BatchProcessor")
@patch("tirajira.commands.resume.TaskCreator")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_success_processing(
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
    mock_json_load,
    mock_file,
    mock_exists,
):
    """Тест: успешная обработка неудачных задач"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}],
        "metadata": {"source_file": "original.json"},
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (1, [{"status": "success"}])
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 5
    args.delay = 2.0
    args.stop_on_error = True
    args.verbose = True
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with(
        "Найдено 1 неудачных задач для повторной обработки"
    )
    mock_logger.success.assert_called_once_with("Успешно обработано 1 из 1 задач")

    # Проверяем, что компоненты были созданы правильно
    mock_jira_client.assert_called_once_with(verbose=True)
    mock_batch_processor.assert_called_once_with(
        mock_jira_client_instance,
        batch_size=5,
        delay=2.0,
        stop_on_error=True,
        verbose=True,
    )
    mock_task_creator.assert_called_once_with(
        jira_client=mock_jira_client_instance,
        batch_processor=mock_batch_processor_instance,
        verbose=True,
    )

    # Проверяем, что метод process был вызван с правильными аргументами
    mock_batch_processor_instance.process.assert_called_once()


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.JiraClient")
@patch("tirajira.commands.resume.BatchProcessor")
@patch("tirajira.commands.resume.TaskCreator")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_with_report_generation(
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
    mock_json_load,
    mock_file,
    mock_exists,
):
    """Тест: обработка неудачных задач с генерацией отчета"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}],
        "metadata": {"source_file": "original.json"},
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (1, [{"status": "success"}])
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Настраиваем аргументы с отчетом
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = "new_report.json"

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что метод _save_report был вызван
    # Поскольку _save_report вызывается у task_creator, проверяем вызов метода
    mock_task_creator_instance._save_report.assert_called_once()


def test_resume_command_extract_failed_tasks_json():
    """Тест: извлечение неудачных задач из JSON отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные
    tasks = [
        {"status": "success", "issue_data": {"summary": "Success task"}},
        {"status": "failure", "issue_data": {"summary": "Failed task 1"}},
        {"status": "failure", "issue_data": {"summary": "Failed task 2"}},
        {"status": "success", "issue_data": {"summary": "Another success task"}},
    ]

    # Вызываем метод извлечения
    result = command._extract_failed_tasks(tasks)

    # Проверяем результат
    assert len(result) == 2
    assert result[0]["summary"] == "Failed task 1"
    assert result[1]["summary"] == "Failed task 2"


def test_resume_command_extract_failed_tasks_csv():
    """Тест: извлечение неудачных задач из CSV/Excel отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.csv"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные в формате CSV/Excel отчета
    # Только поля с префиксом "tasks.", без поля "status"
    tasks = [
        {
            "tasks.status": "success",
            "tasks.summary": "Success task",
            "tasks.project.key": "PROJ",
        },
        {
            "tasks.status": "failure",
            "tasks.summary": "Failed task 1",
            "tasks.project.key": "PROJ",
        },
        {
            "tasks.status": "failure",
            "tasks.summary": "Failed task 2",
            "tasks.project.key": "PROJ",
        },
    ]

    # Вызываем метод извлечения
    result = command._extract_failed_tasks(tasks)

    # Проверяем результат
    assert len(result) == 2
    assert result[0]["summary"] == "Failed task 1"
    assert result[1]["summary"] == "Failed task 2"
    assert result[0]["project.key"] == "PROJ"
    assert result[1]["project.key"] == "PROJ"


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open", new_callable=mock_open, read_data="invalid json"
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_invalid_json(
    mock_get_logger, mock_json_load, mock_file, mock_exists
):
    """Тест: обработка недопустимого JSON в файле отчета"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.side_effect = ValueError("Invalid JSON")
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "invalid.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 1

    # Проверяем, что логгер записал ошибку
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once()


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.JiraClient")
@patch("tirajira.commands.resume.BatchProcessor")
@patch("tirajira.commands.resume.TaskCreator")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_with_yaml_report(
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
    mock_json_load,
    mock_file,
    mock_exists,
):
    """Тест: обработка неудачных задач из YAML отчета"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}],
        "metadata": {"source_file": "original.yaml"},
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (1, [{"status": "success"}])
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.yaml"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with(
        "Найдено 1 неудачных задач для повторной обработки"
    )
    mock_logger.success.assert_called_once_with("Успешно обработано 1 из 1 задач")


@patch("tirajira.commands.resume.os.path.exists")
@patch("tirajira.commands.resume.create_file_loader")
@patch("tirajira.commands.resume.JiraClient")
@patch("tirajira.commands.resume.BatchProcessor")
@patch("tirajira.commands.resume.TaskCreator")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_with_csv_report(
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
    mock_create_file_loader,
    mock_exists,
):
    """Тест: обработка неудачных задач из CSV отчета"""
    # Настраиваем mock
    mock_exists.return_value = True

    # Настраиваем mock для загрузчика файлов
    mock_loader = Mock()
    mock_loader.load_issues.return_value = [
        {
            "tasks.status": "failure",
            "tasks.summary": "Failed task",
            "tasks.project.key": "PROJ",
        }
    ]
    mock_create_file_loader.return_value = mock_loader

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (1, [{"status": "success"}])
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.csv"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with(
        "Найдено 1 неудачных задач для повторной обработки"
    )
    mock_logger.success.assert_called_once_with("Успешно обработано 1 из 1 задач")


@patch("tirajira.commands.resume.os.path.exists")
@patch(
    "tirajira.commands.resume.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.resume.JiraClient")
@patch("tirajira.commands.resume.BatchProcessor")
@patch("tirajira.commands.resume.TaskCreator")
@patch("tirajira.commands.resume.get_logger")
def test_resume_command_with_report_generation_and_source_file(
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
    mock_json_load,
    mock_file,
    mock_exists,
):
    """Тест: обработка неудачных задач с генерацией отчета и
    использованием source_file"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}],
        "metadata": {"source_file": "original.json"},
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor_instance.process.return_value = (1, [{"status": "success"}])
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Настраиваем аргументы с отчетом
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = "new_report.json"

    # Создаем команду и выполняем её
    command = ResumeCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что метод _save_report был вызван с правильным source_file
    mock_task_creator_instance._save_report.assert_called_once_with(
        "original.json",  # source_file из метаданных
        [{"status": "success"}],  # processing_details
        "new_report.json",  # report_file
        1,  # successful_count
        1,  # total_count
    )


def test_resume_command_load_json_report_success():
    """Тест: успешная загрузка JSON отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные
    json_data = (
        '{"tasks": [{"status": "failure", "issue_data": '
        '{"summary": "Failed task"}}], "metadata": {"source_file": "original.json"}}'
    )

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.resume.open", mock_open(read_data=json_data)):
        result = command._load_json_report("report.json")

        # Проверяем результат
        assert "tasks" in result
        assert "metadata" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["status"] == "failure"
        assert result["metadata"]["source_file"] == "original.json"


def test_resume_command_load_json_report_invalid_format():
    """Тест: загрузка JSON отчета с недопустимым форматом"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные - массив вместо объекта
    json_data = '[{"status": "failure"}]'

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.resume.open", mock_open(read_data=json_data)):
        with pytest.raises(Exception) as exc_info:
            command._load_json_report("report.json")

        # Проверяем сообщение об ошибке
        assert "JSON файл отчета должен содержать объект" in str(exc_info.value)


def test_resume_command_load_json_report_invalid_json():
    """Тест: загрузка недопустимого JSON отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные - недопустимый JSON
    json_data = '{"tasks": [{status: "failure"}]'  # Недопустимый JSON

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.resume.open", mock_open(read_data=json_data)):
        with pytest.raises(ValueError) as exc_info:
            command._load_json_report("report.json")

        # Проверяем сообщение об ошибке
        assert "Ошибка парсинга JSON файла отчета" in str(exc_info.value)


def test_resume_command_load_yaml_report_success():
    """Тест: успешная загрузка YAML отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.yaml"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные
    yaml_data = """
tasks:
  - status: failure
    issue_data:
      summary: Failed task
metadata:
  source_file: original.yaml
"""

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.resume.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.resume.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = {
                "tasks": [
                    {"status": "failure", "issue_data": {"summary": "Failed task"}}
                ],
                "metadata": {"source_file": "original.yaml"},
            }
            result = command._load_yaml_report("report.yaml")

            # Проверяем результат
            assert "tasks" in result
            assert "metadata" in result
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["status"] == "failure"
            assert result["metadata"]["source_file"] == "original.yaml"


def test_resume_command_load_yaml_report_invalid_format():
    """Тест: загрузка YAML отчета с недопустимым форматом"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.yaml"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Тестовые данные - массив вместо объекта
    yaml_data = """
- status: failure
"""

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.resume.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.resume.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = [{"status": "failure"}]
            with pytest.raises(Exception) as exc_info:
                command._load_yaml_report("report.yaml")

            # Проверяем сообщение об ошибке
            assert "YAML файл отчета должен содержать объект" in str(exc_info.value)


def test_resume_command_extract_failed_tasks_empty_list():
    """Тест: извлечение неудачных задач из пустого списка"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Пустой список задач
    tasks = []

    # Вызываем метод извлечения
    result = command._extract_failed_tasks(tasks)

    # Проверяем результат
    assert len(result) == 0


def test_resume_command_extract_failed_tasks_mixed_status():
    """Тест: извлечение неудачных задач из смешанного списка статусов"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Смешанный список задач
    tasks = [
        {"status": "success", "issue_data": {"summary": "Success task"}},
        {"status": "failure", "issue_data": {"summary": "Failed task 1"}},
        {"status": "pending", "issue_data": {"summary": "Pending task"}},
        {"status": "failure", "issue_data": {"summary": "Failed task 2"}},
        {"status": "completed", "issue_data": {"summary": "Completed task"}},
    ]

    # Вызываем метод извлечения
    result = command._extract_failed_tasks(tasks)

    # Проверяем результат
    assert len(result) == 2
    assert result[0]["summary"] == "Failed task 1"
    assert result[1]["summary"] == "Failed task 2"


def test_resume_command_extract_failed_tasks_no_issue_data():
    """Тест: извлечение неудачных задач без поля issue_data"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Создаем команду
    command = ResumeCommand(args)

    # Задачи без поля issue_data
    tasks = [
        {"status": "failure", "summary": "Failed task", "project": {"key": "PROJ"}},
        {"status": "success", "summary": "Success task", "project": {"key": "PROJ"}},
    ]

    # Вызываем метод извлечения
    result = command._extract_failed_tasks(tasks)

    # Проверяем результат
    assert len(result) == 1
    assert result[0]["summary"] == "Failed task"
    assert result[0]["project"]["key"] == "PROJ"
    assert "status" not in result[0]  # Поле status должно быть удалено
