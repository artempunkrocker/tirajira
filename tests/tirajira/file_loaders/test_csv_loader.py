import csv
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from tirajira.file_loaders.csv_loader import CsvFileLoader


def test_csv_file_loader_success():
    """Тест: успешная загрузка задач из CSV файла"""
    # Подготавливаем тестовые данные CSV
    csv_content = (
        "project.key,summary,description,issuetype.name,"
        "assignee.emailAddress,priority.name,epic_key\n"
        "PROJ,Test task 1,Description 1,Task,developer@example.com,High,PROJ-100\n"
        "PROJ,Test task 2,Description 2,Bug,qa@example.com,Medium,PROJ-101"
    )

    # Создаем mock для DictReader
    mock_reader = MagicMock()
    mock_reader.fieldnames = [
        "project.key",
        "summary",
        "description",
        "issuetype.name",
        "assignee.emailAddress",
        "priority.name",
        "epic_key",
    ]
    mock_reader.__iter__ = Mock(
        return_value=iter(
            [
                {
                    "project.key": "PROJ",
                    "summary": "Test task 1",
                    "description": "Description 1",
                    "issuetype.name": "Task",
                    "assignee.emailAddress": "developer@example.com",
                    "priority.name": "High",
                    "epic_key": "PROJ-100",
                },
                {
                    "project.key": "PROJ",
                    "summary": "Test task 2",
                    "description": "Description 2",
                    "issuetype.name": "Bug",
                    "assignee.emailAddress": "qa@example.com",
                    "priority.name": "Medium",
                    "epic_key": "PROJ-101",
                },
            ]
        )
    )

    # Используем mock для симуляции чтения файла
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with patch("os.path.exists", return_value=True):
            with patch("csv.DictReader", return_value=mock_reader):
                with patch("csv.Sniffer.sniff") as mock_sniffer:
                    # Настраиваем mock для диалекта CSV
                    mock_dialect = csv.excel()
                    mock_dialect.delimiter = ","
                    mock_sniffer.return_value = mock_dialect

                    loader = CsvFileLoader()
                    issues = loader.load_issues("test.csv")

                    # Проверяем, что данные загрузились правильно
                    assert len(issues) == 2
                    assert issues[0]["summary"] == "Test task 1"
                    assert issues[0]["project"]["key"] == "PROJ"
                    assert issues[0]["issuetype"]["name"] == "Task"
                    assert (
                        issues[0]["assignee"]["emailAddress"] == "developer@example.com"
                    )
                    assert issues[0]["priority"]["name"] == "High"
                    assert issues[0]["epic_key"] == "PROJ-100"

                    assert issues[1]["summary"] == "Test task 2"
                    assert issues[1]["issuetype"]["name"] == "Bug"
                    assert issues[1]["assignee"]["emailAddress"] == "qa@example.com"
                    assert issues[1]["priority"]["name"] == "Medium"
                    assert issues[1]["epic_key"] == "PROJ-101"


def test_csv_file_loader_file_not_found():
    """Тест: обработка ошибки файла не найден для CSV"""
    with patch("os.path.exists", return_value=False):
        loader = CsvFileLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_issues("nonexistent.csv")


def test_csv_file_loader_invalid_csv():
    """Тест: обработка ошибки невалидного CSV"""
    with patch(
        "builtins.open", mock_open(read_data="invalid,csv,content\nunclosed,quote")
    ):
        with patch("os.path.exists", return_value=True):
            with patch("csv.Sniffer.sniff") as mock_sniffer:
                # Настраиваем mock для диалекта CSV
                mock_dialect = csv.excel()
                mock_dialect.delimiter = ","
                mock_sniffer.return_value = mock_dialect

                # Мокируем DictReader чтобы он выбросил csv.Error
                with patch("csv.DictReader") as mock_dict_reader:
                    mock_dict_reader.side_effect = csv.Error("Неверный формат CSV")

                    loader = CsvFileLoader()
                    with pytest.raises(ValueError, match="Ошибка парсинга CSV файла"):
                        loader.load_issues("test.csv")


def test_csv_file_loader_empty_file():
    """Тест: обработка пустого CSV файла"""
    # Мокируем DictReader с None fieldnames
    mock_reader = MagicMock()
    mock_reader.fieldnames = None

    with patch("builtins.open", mock_open(read_data="")):
        with patch("os.path.exists", return_value=True):
            with patch("csv.DictReader", return_value=mock_reader):
                with patch("csv.Sniffer.sniff") as mock_sniffer:
                    # Настраиваем mock для диалекта CSV
                    mock_dialect = csv.excel()
                    mock_dialect.delimiter = ","
                    mock_sniffer.return_value = mock_dialect

                    loader = CsvFileLoader()
                    with pytest.raises(
                        Exception,
                        match="Ошибка при чтении файла: CSV файл пуст или поврежден",
                    ):
                        loader.load_issues("empty.csv")


def test_csv_file_loader_skip_empty_rows():
    """Тест: пропуск пустых строк в CSV файле"""
    # Подготавливаем тестовые данные CSV с пустыми строками
    csv_content = """project.key,summary
PROJ,Task 1

PROJ,Task 2"""

    # Создаем mock для DictReader с пустыми строками
    mock_reader = MagicMock()
    mock_reader.fieldnames = ["project.key", "summary"]
    mock_reader.__iter__ = Mock(
        return_value=iter(
            [
                {"project.key": "PROJ", "summary": "Task 1"},
                {"project.key": "", "summary": ""},  # Пустая строка
                {"project.key": "PROJ", "summary": "Task 2"},
            ]
        )
    )

    # Используем mock для симуляции чтения файла
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with patch("os.path.exists", return_value=True):
            with patch("csv.DictReader", return_value=mock_reader):
                with patch("csv.Sniffer.sniff") as mock_sniffer:
                    # Настраиваем mock для диалекта CSV
                    mock_dialect = csv.excel()
                    mock_dialect.delimiter = ","
                    mock_sniffer.return_value = mock_dialect

                    loader = CsvFileLoader()
                    issues = loader.load_issues("test.csv")

                    # Проверяем, что пустые строки были пропущены
                    assert len(issues) == 2
                    assert issues[0]["project"]["key"] == "PROJ"
                    assert issues[0]["summary"] == "Task 1"
                    assert issues[1]["project"]["key"] == "PROJ"
                    assert issues[1]["summary"] == "Task 2"


def test_csv_file_loader_general_exception():
    """Тест: обработка общих исключений при чтении файла."""
    with patch("builtins.open", side_effect=Exception("Ошибка файловой системы")):
        with patch("os.path.exists", return_value=True):
            loader = CsvFileLoader()
            with pytest.raises(
                Exception, match="Ошибка при чтении файла: Ошибка файловой системы"
            ):
                loader.load_issues("test.csv")


def test_csv_file_loader_nested_dict_conversion():
    """Тест: преобразование вложенных словарей с точечной нотацией."""
    # Подготавливаем тестовые данные CSV с вложенными ключами
    csv_content = """project.key,issuetype.name,assignee.emailAddress,simple_key
PROJ,Task,user@example.com,value"""

    # Создаем mock для DictReader
    mock_reader = MagicMock()
    mock_reader.fieldnames = [
        "project.key",
        "issuetype.name",
        "assignee.emailAddress",
        "simple_key",
    ]
    mock_reader.__iter__ = Mock(
        return_value=iter(
            [
                {
                    "project.key": "PROJ",
                    "issuetype.name": "Task",
                    "assignee.emailAddress": "user@example.com",
                    "simple_key": "value",
                }
            ]
        )
    )

    # Используем mock для симуляции чтения файла
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with patch("os.path.exists", return_value=True):
            with patch("csv.DictReader", return_value=mock_reader):
                with patch("csv.Sniffer.sniff") as mock_sniffer:
                    # Настраиваем mock для диалекта CSV
                    mock_dialect = csv.excel()
                    mock_dialect.delimiter = ","
                    mock_sniffer.return_value = mock_dialect

                    loader = CsvFileLoader()
                    issues = loader.load_issues("test.csv")

                    # Проверяем, что данные загрузились правильно с вложенными словарями
                    assert len(issues) == 1
                    assert issues[0]["project"]["key"] == "PROJ"
                    assert issues[0]["issuetype"]["name"] == "Task"
                    assert issues[0]["assignee"]["emailAddress"] == "user@example.com"
                    assert issues[0]["simple_key"] == "value"
