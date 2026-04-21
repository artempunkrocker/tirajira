from unittest.mock import mock_open, patch

import pytest
import yaml

from tirajira.file_loaders.yaml_loader import YamlFileLoader


def test_yaml_file_loader_success():
    """Тест: успешная загрузка задач из YAML файла"""
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

    # Преобразуем данные в YAML строку
    yaml_content = yaml.dump(test_data, allow_unicode=True)

    # Используем mock для симуляции чтения файла
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        with patch("os.path.exists", return_value=True):
            loader = YamlFileLoader()
            issues = loader.load_issues("test.yaml")

            # Проверяем, что данные загрузились правильно
            assert len(issues) == 2
            assert issues[0]["summary"] == "Test task 1"
            assert issues[1]["issuetype"]["name"] == "Bug"


def test_yaml_file_loader_file_not_found():
    """Тест: обработка ошибки файла не найден"""
    with patch("os.path.exists", return_value=False):
        loader = YamlFileLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_issues("nonexistent.yaml")


def test_yaml_file_loader_invalid_yaml():
    """Тест: обработка ошибки невалидного YAML"""
    with patch("builtins.open", mock_open(read_data="invalid: yaml: content:")):
        with patch("os.path.exists", return_value=True):
            loader = YamlFileLoader()
            with pytest.raises(ValueError, match="Ошибка парсинга YAML файла"):
                loader.load_issues("test.yaml")


def test_yaml_file_loader_not_list():
    """Тест: обработка ошибки, когда YAML не содержит массив"""
    # YAML с объектом вместо массива
    yaml_content = "project: PROJ\nsummary: Test task"

    with patch("builtins.open", mock_open(read_data=yaml_content)):
        with patch("os.path.exists", return_value=True):
            loader = YamlFileLoader()
            with pytest.raises(
                ValueError, match="YAML файл должен содержать массив задач"
            ):
                loader.load_issues("test.yaml")


def test_yaml_file_loader_general_exception():
    """Тест: обработка общих исключений при чтении файла."""
    with patch("builtins.open", side_effect=Exception("Ошибка файловой системы")):
        with patch("os.path.exists", return_value=True):
            loader = YamlFileLoader()
            with pytest.raises(
                Exception, match="Ошибка при чтении файла: Ошибка файловой системы"
            ):
                loader.load_issues("test.yaml")
