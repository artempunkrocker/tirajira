import os
from unittest.mock import Mock, patch

import pytest

from tirajira.main import create_tasks_from_file, main


@patch("tirajira.main.TaskCreator")
@patch("tirajira.main.BatchProcessor")
@patch("tirajira.main.JiraClient")
def test_create_tasks_from_file_success(
    mock_jira_client, mock_batch_processor, mock_task_creator
):
    """Тест: успешное создание задач из файла"""
    # Подготавливаем mock объекты
    mock_task_creator_instance = Mock()
    mock_task_creator_instance.create_from_file.return_value = 1
    mock_task_creator.return_value = mock_task_creator_instance

    # Вызываем тестируемую функцию
    create_tasks_from_file("test.json")

    # Проверяем, что методы были вызваны правильно
    mock_jira_client.assert_called_once()
    mock_batch_processor.assert_called_once()
    mock_task_creator.assert_called_once()
    mock_task_creator_instance.create_from_file.assert_called_once_with(
        file_path="test.json",
        batch_size=10,
        delay=1.0,
        stop_on_error=False,
        verbose=False,
        report_file=None,
    )


@patch("tirajira.main.TaskCreator")
@patch("tirajira.main.BatchProcessor")
@patch("tirajira.main.JiraClient")
def test_create_tasks_from_file_not_found(
    mock_jira_client, mock_batch_processor, mock_task_creator
):
    """Тест: обработка ошибки файла не найден"""
    # Настраиваем mock чтобы выбрасывал исключение
    mock_task_creator_instance = Mock()
    mock_task_creator_instance.create_from_file.side_effect = FileNotFoundError(
        "Файл test.json не найден."
    )
    mock_task_creator.return_value = mock_task_creator_instance

    # Проверяем, что функция завершается с кодом 1
    with pytest.raises(SystemExit) as excinfo:
        create_tasks_from_file("test.json")
    assert excinfo.value.code == 1


def test_main_no_args(capsys):
    """Тест: вызов без аргументов выводит справку"""
    with patch("sys.argv", ["main.py"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Проверяем, что код выхода равен 1
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    # Проверяем наличие ключевых элементов справки
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


def test_main_with_file_arg():
    """Тест: вызов с аргументом файла через команду import"""
    # Проверяем, что программа запускается без ошибок с правильными аргументами
    with patch("sys.argv", ["main.py", "import", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Проверяем, что код выхода равен 0 (успешное завершение для --help)
        assert exc_info.value.code == 0


def test_main_with_help_arg(capsys):
    """Тест: вызов с аргументом --help выводит справку"""
    with patch("sys.argv", ["main.py", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Проверяем, что код выхода равен 0 (успешное завершение для --help)
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    # Проверяем наличие ключевых элементов справки
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


def test_main_with_version_arg(capsys):
    """Тест: вызов с аргументом --version выводит версию"""
    with patch("sys.argv", ["main.py", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Проверяем, что код выхода равен 0 (успешное завершение для --version)
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "tirajira" in captured.out


def test_main_with_short_version_arg(capsys):
    """Тест: вызов с аргументом --version выводит версию"""
    with patch("sys.argv", ["main.py", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Проверяем, что код выхода равен 0 (успешное завершение для --version)
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "tirajira" in captured.out


def test_main_module_execution():
    """Тест: выполнение модуля как скрипт"""
    # Проверяем, что модуль может быть импортирован без ошибок
    from tirajira import main

    assert main is not None


def test_main_with_empty_argv(monkeypatch, capsys):
    """Тест: вызов с пустым sys.argv"""
    monkeypatch.setattr("sys.argv", ["main.py"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    # Проверяем, что код выхода равен 1
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    # Проверяем наличие ключевых элементов справки
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


def test_main_with_help_argument(monkeypatch, capsys):
    """Тест: вызов с аргументом --help"""
    monkeypatch.setattr("sys.argv", ["main.py", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    # Проверяем, что код выхода равен 0 (успешное завершение для --help)
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    # Проверяем наличие ключевых элементов справки
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_file_argument(mock_import_command, monkeypatch):
    """Тест: вызов с аргументом файла"""
    monkeypatch.setattr("sys.argv", ["main.py", "import", "test.json"])
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_batch_size_argument(mock_import_command, monkeypatch):
    """Тест: вызов с аргументом размера пакета"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "--batch-size", "5"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_delay_argument(mock_import_command, monkeypatch):
    """Тест: вызов с аргументом задержки"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "--delay", "2.5"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_both_arguments(mock_import_command, monkeypatch):
    """Тест: вызов с обоими аргументами"""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "import", "test.json", "--batch-size", "3", "--delay", "0.5"],
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_short_arguments(mock_import_command, monkeypatch):
    """Тест: вызов с сокращенными аргументами"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "-b", "7", "-d", "1.5"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_stop_on_error_argument(mock_import_command, monkeypatch):
    """Тест: вызов с аргументом --stop-on-error"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "--stop-on-error"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_all_arguments(mock_import_command, monkeypatch):
    """Тест: вызов со всеми аргументами"""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "import", "test.json", "-b", "5", "-d", "2.0", "--stop-on-error"],
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Проверяем, что ImportCommand был создан и вызван
    mock_import_command.assert_called_once()
    mock_import_command_instance.execute.assert_called_once()


def test_main_successful_execution(monkeypatch):
    """Тест: проверка успешного выполнения main() без исключений"""

    # Создаем фиктивную функцию для cli_main, которая не вызывает исключений
    def mock_cli_main():
        pass

    # Патчим cli_main
    with patch("tirajira.main.cli_main", side_effect=mock_cli_main):
        # Проверяем, что main() выполняется без исключений
        try:
            main()
            # Если мы здесь, значит исключения не было
            assert True
        except Exception as e:
            # Если произошло исключение, тест должен провалиться
            raise AssertionError(f"main() вызвал исключение: {e}") from e
