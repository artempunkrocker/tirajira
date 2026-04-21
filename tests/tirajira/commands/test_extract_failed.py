"""
Тесты для команды извлечения неудачных задач TiraJira.
"""

from unittest.mock import Mock, mock_open, patch

import pytest

from tirajira.commands.extract_failed import ExtractFailedCommand


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_file_not_found(mock_get_logger, mock_exists):
    """Тест: обработка случая, когда файл отчета не найден"""
    # Настраиваем mock
    mock_exists.return_value = False
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "nonexistent.json"
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 1

    # Проверяем, что логгер записал ошибку
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once_with("Файл отчета nonexistent.json не найден")


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_no_failed_tasks(
    mock_get_logger, mock_json_load, mock_file, mock_exists
):
    """Тест: обработка случая, когда в отчете нет неудачных задач"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {"tasks": []}
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with("Не найдено неудачных задач в отчете")


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "success"}]}',
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_success(
    mock_get_logger, mock_create_report_writer, mock_json_load, mock_file, mock_exists
):
    """Тест: успешное извлечение неудачных задач"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [
            {"status": "success", "issue_data": {"summary": "Success task"}},
            {"status": "failure", "issue_data": {"summary": "Failed task"}},
        ]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with("Найдено 1 неудачных задач")
    mock_logger.success.assert_called_once_with(
        "Извлеченные задачи сохранены в файл: failed.json"
    )

    # Проверяем, что writer был вызван правильно
    mock_create_report_writer.assert_called_once_with("json")
    mock_writer.write_report.assert_called_once()


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch("tirajira.commands.extract_failed.open", new_callable=mock_open, read_data="{}")
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.get_logger")
@patch("tirajira.commands.extract_failed.create_file_loader")
def test_extract_failed_command_exception_handling(
    mock_create_file_loader, mock_get_logger, mock_json_load, mock_file, mock_exists
):
    """Тест: обработка исключений в команде извлечения неудачных задач"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.side_effect = Exception("Ошибка чтения файла")
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем аргументы
    args = Mock()
    args.report_file = "corrupted.json"
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 1

    # Проверяем, что логгер записал ошибку
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once()


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data="invalid json",
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_invalid_json(
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
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 1

    # Проверяем, что логгер записал ошибку
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once()


def test_extract_failed_command_extract_failed_tasks_json():
    """Тест: извлечение неудачных задач из JSON отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

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


def test_extract_failed_command_extract_failed_tasks_csv():
    """Тест: извлечение неудачных задач из CSV/Excel отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.csv"
    args.output_file = "failed.csv"

    # Создаем команду
    command = ExtractFailedCommand(args)

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


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_output_file_without_extension(
    mock_get_logger, mock_create_report_writer, mock_json_load, mock_file, mock_exists
):
    """Тест: создание выходного файла с автоматическим добавлением расширения"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Настраиваем аргументы без расширения
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed"  # Без расширения

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что имя файла было обновлено с расширением
    assert args.output_file == "failed.json"


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_with_yaml_report(
    mock_get_logger, mock_create_report_writer, mock_json_load, mock_file, mock_exists
):
    """Тест: извлечение неудачных задач из YAML отчета"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Настраиваем аргументы с YAML файлом
    args = Mock()
    args.report_file = "report.yaml"
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with("Найдено 1 неудачных задач")
    mock_logger.success.assert_called_once_with(
        "Извлеченные задачи сохранены в файл: failed.json"
    )


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch("tirajira.commands.extract_failed.create_file_loader")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_with_csv_report(
    mock_get_logger, mock_create_report_writer, mock_create_file_loader, mock_exists
):
    """Тест: извлечение неудачных задач из CSV отчета"""
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

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Настраиваем аргументы с CSV файлом
    args = Mock()
    args.report_file = "report.csv"
    args.output_file = "failed.json"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что логгер записал информацию
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with("Найдено 1 неудачных задач")
    mock_logger.success.assert_called_once_with(
        "Извлеченные задачи сохранены в файл: failed.json"
    )


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_with_custom_output_format(
    mock_get_logger, mock_create_report_writer, mock_json_load, mock_file, mock_exists
):
    """Тест: извлечение неудачных задач с сохранением в разных форматах"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Настраиваем аргументы с выходным файлом в формате YAML
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.yaml"

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что создатель отчетов был вызван с правильным форматом
    mock_create_report_writer.assert_called_once_with("yaml")


@patch("tirajira.commands.extract_failed.os.path.exists")
@patch(
    "tirajira.commands.extract_failed.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.extract_failed.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.commands.extract_failed.get_logger")
def test_extract_failed_command_with_unsupported_output_format(
    mock_get_logger, mock_create_report_writer, mock_json_load, mock_file, mock_exists
):
    """Тест: извлечение неудачных задач с сохранением в неподдерживаемом формате"""
    # Настраиваем mock
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Настраиваем аргументы с выходным файлом в неподдерживаемом формате
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.txt"  # Неподдерживаемый формат

    # Создаем команду и выполняем её
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Проверяем результат
    assert result == 0

    # Проверяем, что создатель отчетов был вызван с форматом JSON (по умолчанию)
    mock_create_report_writer.assert_called_once_with("json")


def test_extract_failed_command_load_json_report_success():
    """Тест: успешная загрузка JSON отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

    # Тестовые данные
    json_data = (
        '{"tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]}'
    )

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.extract_failed.open", mock_open(read_data=json_data)):
        result = command._load_json_report("report.json")

        # Проверяем результат
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["status"] == "failure"


def test_extract_failed_command_load_json_report_invalid_format():
    """Тест: загрузка JSON отчета с недопустимым форматом"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

    # Тестовые данные - массив вместо объекта
    json_data = '[{"status": "failure"}]'

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.extract_failed.open", mock_open(read_data=json_data)):
        with pytest.raises(Exception) as exc_info:
            command._load_json_report("report.json")

        # Проверяем сообщение об ошибке
        assert "JSON файл отчета должен содержать объект" in str(exc_info.value)


def test_extract_failed_command_load_json_report_invalid_json():
    """Тест: загрузка недопустимого JSON отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

    # Тестовые данные - недопустимый JSON
    json_data = '{"tasks": [{status: "failure"}]'  # Недопустимый JSON

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.extract_failed.open", mock_open(read_data=json_data)):
        with pytest.raises(ValueError) as exc_info:
            command._load_json_report("report.json")

        # Проверяем сообщение об ошибке
        assert "Ошибка парсинга JSON файла отчета" in str(exc_info.value)


def test_extract_failed_command_load_yaml_report_success():
    """Тест: успешная загрузка YAML отчета"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.yaml"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

    # Тестовые данные
    yaml_data = """
tasks:
  - status: failure
    issue_data:
      summary: Failed task
"""

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.extract_failed.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.extract_failed.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = {
                "tasks": [
                    {"status": "failure", "issue_data": {"summary": "Failed task"}}
                ]
            }
            result = command._load_yaml_report("report.yaml")

            # Проверяем результат
            assert "tasks" in result
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["status"] == "failure"


def test_extract_failed_command_load_yaml_report_invalid_format():
    """Тест: загрузка YAML отчета с недопустимым форматом"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.yaml"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

    # Тестовые данные - массив вместо объекта
    yaml_data = """
- status: failure
"""

    # Используем patch для имитации чтения файла
    with patch("tirajira.commands.extract_failed.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.extract_failed.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = [{"status": "failure"}]
            with pytest.raises(Exception) as exc_info:
                command._load_yaml_report("report.yaml")

            # Проверяем сообщение об ошибке
            assert "YAML файл отчета должен содержать объект" in str(exc_info.value)


def test_extract_failed_command_extract_failed_tasks_empty_list():
    """Тест: извлечение неудачных задач из пустого списка"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

    # Пустой список задач
    tasks = []

    # Вызываем метод извлечения
    result = command._extract_failed_tasks(tasks)

    # Проверяем результат
    assert len(result) == 0


def test_extract_failed_command_extract_failed_tasks_mixed_status():
    """Тест: извлечение неудачных задач из смешанного списка статусов"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

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


def test_extract_failed_command_extract_failed_tasks_no_issue_data():
    """Тест: извлечение неудачных задач без поля issue_data"""
    # Настраиваем аргументы
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Создаем команду
    command = ExtractFailedCommand(args)

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
