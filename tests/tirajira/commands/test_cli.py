"""
Тесты для CLI интерфейса TiraJira.
"""

from unittest.mock import Mock, patch

import pytest

from tirajira.commands.cli import create_argument_parser, main


def test_create_argument_parser():
    """Тест: создание парсера аргументов"""
    parser = create_argument_parser()

    # Проверяем, что парсер создан
    assert parser is not None

    # Проверяем наличие основных элементов
    assert parser.prog == "tirajira"
    assert (
        "Инструмент для автоматизации массового создания задач в Jira"
        in parser.description
    )


def test_parser_import_command():
    """Тест: парсинг команды import"""
    parser = create_argument_parser()

    # Тест с минимальными аргументами
    args = parser.parse_args(["import", "test.json"])
    assert args.command == "import"
    assert args.file == "test.json"
    assert args.batch_size == 10
    assert args.delay == 1.0
    assert args.stop_on_error is False
    assert args.verbose is False
    assert args.report is None


def test_parser_import_command_with_options():
    """Тест: парсинг команды import с опциями"""
    parser = create_argument_parser()

    # Тест с полным набором аргументов
    args = parser.parse_args(
        [
            "import",
            "test.json",
            "--batch-size",
            "5",
            "--delay",
            "2.5",
            "--stop-on-error",
            "--verbose",
            "--report",
            "report.json",
        ]
    )

    assert args.command == "import"
    assert args.file == "test.json"
    assert args.batch_size == 5
    assert args.delay == 2.5
    assert args.stop_on_error is True
    assert args.verbose is True
    assert args.report == "report.json"


def test_parser_import_command_with_short_options():
    """Тест: парсинг команды import с короткими опциями"""
    parser = create_argument_parser()

    # Тест с короткими аргументами
    args = parser.parse_args(["import", "test.json", "-b", "3", "-d", "1.5", "-v"])

    assert args.command == "import"
    assert args.file == "test.json"
    assert args.batch_size == 3
    assert args.delay == 1.5
    assert args.verbose is True


def test_parser_extract_failed_command():
    """Тест: парсинг команды extract-failed"""
    parser = create_argument_parser()

    # Тест с аргументами команды extract-failed
    args = parser.parse_args(["extract-failed", "report.json", "failed.json"])

    assert args.command == "extract-failed"
    assert args.report_file == "report.json"
    assert args.output_file == "failed.json"


def test_parser_resume_command():
    """Тест: парсинг команды resume"""
    parser = create_argument_parser()

    # Тест с аргументами команды resume
    args = parser.parse_args(["resume", "report.json"])

    assert args.command == "resume"
    assert args.report_file == "report.json"


def test_parser_resume_command_with_options():
    """Тест: парсинг команды resume с опциями"""
    parser = create_argument_parser()

    # Тест с аргументами команды resume и опциями
    args = parser.parse_args(
        [
            "resume",
            "report.json",
            "--batch-size",
            "7",
            "--delay",
            "0.5",
            "--stop-on-error",
            "--verbose",
            "--report",
            "new_report.json",
        ]
    )

    assert args.command == "resume"
    assert args.report_file == "report.json"
    assert args.batch_size == 7
    assert args.delay == 0.5
    assert args.stop_on_error is True
    assert args.verbose is True
    assert args.report == "new_report.json"


def test_parser_version_argument():
    """Тест: парсинг аргумента --version"""
    parser = create_argument_parser()

    # Тест с аргументом --version
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])

    # Для аргумента --version argparse вызывает SystemExit с кодом 0
    assert exc_info.value.code == 0


@patch("tirajira.commands.cli.ImportCommand")
def test_main_import_command(mock_import_command):
    """Тест: выполнение команды import через main"""
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance

    with patch("sys.argv", ["tirajira", "import", "test.json"]):
        main()

        # Проверяем, что ImportCommand был создан и вызван
        mock_import_command.assert_called_once()
        mock_import_command_instance.execute.assert_called_once()


@patch("tirajira.commands.cli.ExtractFailedCommand")
def test_main_extract_failed_command(mock_extract_failed_command):
    """Тест: выполнение команды extract-failed через main"""
    mock_extract_failed_command_instance = Mock()
    mock_extract_failed_command.return_value = mock_extract_failed_command_instance

    with patch(
        "sys.argv", ["tirajira", "extract-failed", "report.json", "failed.json"]
    ):
        main()

        # Проверяем, что ExtractFailedCommand был создан и вызван
        mock_extract_failed_command.assert_called_once()
        mock_extract_failed_command_instance.execute.assert_called_once()


@patch("tirajira.commands.cli.ResumeCommand")
def test_main_resume_command(mock_resume_command):
    """Тест: выполнение команды resume через main"""
    mock_resume_command_instance = Mock()
    mock_resume_command.return_value = mock_resume_command_instance

    with patch("sys.argv", ["tirajira", "resume", "report.json"]):
        main()

        # Проверяем, что ResumeCommand был создан и вызван
        mock_resume_command.assert_called_once()
        mock_resume_command_instance.execute.assert_called_once()


def test_main_no_command(capsys):
    """Тест: выполнение без команды выводит справку"""
    with patch("sys.argv", ["tirajira"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Проверяем, что код выхода равен 1
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        # Проверяем наличие справки
        assert "usage: tirajira" in captured.out


@patch("argparse.ArgumentParser.print_help")
def test_main_help_command(mock_print_help):
    """Тест: выполнение с командой help"""
    with patch("sys.argv", ["tirajira", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Проверяем, что код выхода равен 0
        assert exc_info.value.code == 0

        # Проверяем, что print_help был вызван
        mock_print_help.assert_called_once()
