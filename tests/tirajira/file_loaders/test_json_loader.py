import json
from unittest.mock import mock_open, patch

import pytest

from tirajira.file_loaders.json_loader import JsonFileLoader


def test_json_file_loader_success():
    """Тест: успешная загрузка задач из JSON файла"""
    # Подготавливаем тестовые данные
    test_data = [
        {
            "project": {"key": "PROJ"},
            "summary": "Test task 1",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Test task 2",
            "issuetype": {"name": "Bug"},
        },
    ]

    # Преобразуем данные в JSON строку
    json_content = json.dumps(test_data, ensure_ascii=False)

    # Используем mock для симуляции чтения файла
    with patch("builtins.open", mock_open(read_data=json_content)):
        with patch("os.path.exists", return_value=True):
            loader = JsonFileLoader()
            issues = loader.load_issues("test.json")

            # Проверяем, что данные загрузились правильно
            assert len(issues) == 2
            assert issues[0]["summary"] == "Test task 1"
            assert issues[1]["issuetype"]["name"] == "Bug"


def test_json_file_loader_file_not_found():
    """Тест: обработка ошибки файла не найден"""
    with patch("os.path.exists", return_value=False):
        loader = JsonFileLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_issues("nonexistent.json")


def test_json_file_loader_invalid_json():
    """Тест: обработка ошибки невалидного JSON"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("os.path.exists", return_value=True):
            loader = JsonFileLoader()
            with pytest.raises(ValueError, match="Ошибка парсинга JSON файла"):
                loader.load_issues("test.json")


def test_json_file_loader_not_list():
    """Тест: обработка ошибки, когда JSON не содержит массив"""
    # JSON с объектом вместо массива
    json_content = '{"project": "PROJ", "summary": "Test task"}'

    with patch("builtins.open", mock_open(read_data=json_content)):
        with patch("os.path.exists", return_value=True):
            loader = JsonFileLoader()
            with pytest.raises(
                ValueError, match="JSON файл должен содержать массив задач"
            ):
                loader.load_issues("test.json")


def test_json_file_loader_general_exception():
    """Тест: обработка общих исключений при чтении файла."""
    with patch("builtins.open", side_effect=Exception("Ошибка файловой системы")):
        with patch("os.path.exists", return_value=True):
            loader = JsonFileLoader()
            with pytest.raises(
                Exception, match="Ошибка при чтении файла: Ошибка файловой системы"
            ):
                loader.load_issues("test.json")
