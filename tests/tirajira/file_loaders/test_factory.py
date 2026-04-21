import pytest

from tirajira.file_loaders.csv_loader import CsvFileLoader
from tirajira.file_loaders.excel_loader import ExcelFileLoader
from tirajira.file_loaders.factory import create_file_loader
from tirajira.file_loaders.json_loader import JsonFileLoader
from tirajira.file_loaders.xml_loader import XmlFileLoader
from tirajira.file_loaders.yaml_loader import YamlFileLoader


def test_create_file_loader_json():
    """Тест: создание загрузчика для JSON файла"""
    loader = create_file_loader(".json")
    assert isinstance(loader, JsonFileLoader)


def test_create_file_loader_csv():
    """Тест: создание загрузчика для CSV файла"""
    loader = create_file_loader(".csv")
    assert isinstance(loader, CsvFileLoader)


def test_create_file_loader_yaml():
    """Тест: создание загрузчика для YAML файла"""
    loader = create_file_loader(".yaml")
    assert isinstance(loader, YamlFileLoader)


def test_create_file_loader_yml():
    """Тест: создание загрузчика для YML файла"""
    loader = create_file_loader(".yml")
    assert isinstance(loader, YamlFileLoader)


def test_create_file_loader_xlsx():
    """Тест: создание загрузчика для Excel файла"""
    loader = create_file_loader(".xlsx")
    assert isinstance(loader, ExcelFileLoader)


def test_create_file_loader_xml():
    """Тест: создание загрузчика для XML файла"""
    loader = create_file_loader(".xml")
    assert isinstance(loader, XmlFileLoader)


def test_create_file_loader_case_insensitive():
    """Тест: регистронезависимость расширений файлов"""
    loader1 = create_file_loader(".JSON")
    loader2 = create_file_loader(".Json")
    assert isinstance(loader1, JsonFileLoader)
    assert isinstance(loader2, JsonFileLoader)


def test_create_file_loader_unsupported_format():
    """Тест: обработка неподдерживаемого формата файла"""
    with pytest.raises(ValueError, match="Не поддерживаемый формат файла: .txt"):
        create_file_loader(".txt")


def test_create_file_loader_empty_extension():
    """Тест: обработка пустого расширения файла"""
    with pytest.raises(ValueError, match="Не поддерживаемый формат файла: "):
        create_file_loader("")
