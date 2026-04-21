"""
Тесты для парсера аргументов TiraJira.
"""

import io
from unittest.mock import patch

from tirajira.commands.argument_parser import ArgumentParser


def test_argument_parser_init():
    """Тест: инициализация парсера аргументов"""
    parser = ArgumentParser()

    # Проверяем, что парсер создан
    assert parser is not None
    assert parser.parser is not None


def test_argument_parser_parse_with_file():
    """Тест: парсинг аргументов с указанием файла"""
    parser = ArgumentParser()

    # Имитируем аргументы командной строки
    with patch("sys.argv", ["main.py", "test.json"]):
        args = parser.parse()

        assert args.file_path == "test.json"
        assert args.batch_size == 10  # значение по умолчанию
        assert args.delay == 1.0  # значение по умолчанию
        assert args.stop_on_error is False
        assert args.verbose is False
        assert args.report is None
        assert args.help is False
        assert args.version is False


def test_argument_parser_parse_with_options():
    """Тест: парсинг аргументов с опциями"""
    parser = ArgumentParser()

    # Имитируем аргументы командной строки с опциями
    with patch(
        "sys.argv",
        [
            "main.py",
            "test.json",
            "--batch-size",
            "5",
            "--delay",
            "2.5",
            "--stop-on-error",
            "--verbose",
            "--report",
            "report.json",
        ],
    ):
        args = parser.parse()

        assert args.file_path == "test.json"
        assert args.batch_size == 5
        assert args.delay == 2.5
        assert args.stop_on_error is True
        assert args.verbose is True
        assert args.report == "report.json"


def test_argument_parser_parse_with_short_options():
    """Тест: парсинг аргументов с короткими опциями"""
    parser = ArgumentParser()

    # Создаем аргументы напрямую, чтобы избежать конфликта с pytest
    args = parser.parser.parse_args(["test.json", "-b", "3", "-d", "1.5", "--verbose"])

    assert args.file_path == "test.json"
    assert args.batch_size == 3
    assert args.delay == 1.5
    assert args.verbose is True


def test_argument_parser_parse_report_without_value():
    """Тест: парсинг аргумента --report без значения"""
    parser = ArgumentParser()

    # Имитируем аргументы командной строки с --report без значения
    with patch("sys.argv", ["main.py", "test.json", "--report"]):
        args = parser.parse()

        assert args.file_path == "test.json"
        assert args.report is True  # Когда --report указан без значения


def test_argument_parser_parse_help():
    """Тест: парсинг аргумента --help"""
    parser = ArgumentParser()

    # Имитируем аргументы командной строки с --help
    with patch("sys.argv", ["main.py", "--help"]):
        args = parser.parse()

        assert args.help is True


def test_argument_parser_parse_version():
    """Тест: парсинг аргумента --version"""
    parser = ArgumentParser()

    # Имитируем аргументы командной строки с --version
    with patch("sys.argv", ["main.py", "--version"]):
        args = parser.parse()

        assert args.version is True


def test_argument_parser_handle_special_args_help():
    """Тест: обработка специального аргумента --help"""
    parser = ArgumentParser()

    # Создаем аргументы с --help
    args = parser.parser.parse_args(["--help"])

    # Проверяем, что handle_special_args возвращает True для --help
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        result = parser.handle_special_args(args)

        assert result is True
        output = mock_stdout.getvalue()
        # Проверяем, что вывод содержит справку
        assert "TiraJira (тиражира)" in output


def test_argument_parser_handle_special_args_version():
    """Тест: обработка специального аргумента --version"""
    parser = ArgumentParser()

    # Создаем аргументы с --version
    args = parser.parser.parse_args(["--version"])

    # Проверяем, что handle_special_args возвращает True для --version
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        with patch("tirajira.__version__", "1.0.0"):
            result = parser.handle_special_args(args)

            assert result is True
            output = mock_stdout.getvalue()
            # Проверяем, что вывод содержит версию
            assert "TiraJira version 1.0.0" in output


def test_argument_parser_handle_special_args_no_special():
    """Тест: обработка обычных аргументов (не специальных)"""
    parser = ArgumentParser()

    # Создаем обычные аргументы
    args = parser.parser.parse_args(["test.json"])

    # Проверяем, что handle_special_args возвращает False для обычных аргументов
    result = parser.handle_special_args(args)

    assert result is False


def test_argument_parser_validate_args_valid():
    """Тест: валидация корректных аргументов"""
    parser = ArgumentParser()

    # Создаем аргументы с указанием файла
    args = parser.parser.parse_args(["test.json"])

    # Проверяем, что валидация проходит успешно
    result = parser.validate_args(args)

    assert result is True


def test_argument_parser_validate_args_invalid_no_file():
    """Тест: валидация некорректных аргументов (без файла)"""
    parser = ArgumentParser()

    # Создаем аргументы без указания файла
    args = parser.parser.parse_args([])

    # Проверяем, что валидация не проходит
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        result = parser.validate_args(args)

        assert result is False
        output = mock_stdout.getvalue()
        # Проверяем, что вывод содержит сообщение об ошибке
        assert "Ошибка: Не указан путь к файлу с задачами" in output
