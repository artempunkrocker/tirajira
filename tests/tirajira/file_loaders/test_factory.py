import pytest

from tirajira.file_loaders.csv_loader import CsvFileLoader
from tirajira.file_loaders.excel_loader import ExcelFileLoader
from tirajira.file_loaders.factory import create_file_loader
from tirajira.file_loaders.json_loader import JsonFileLoader
from tirajira.file_loaders.xml_loader import XmlFileLoader
from tirajira.file_loaders.yaml_loader import YamlFileLoader


def test_create_file_loader_json():
    """Test: creating a loader for JSON file"""
    loader = create_file_loader(".json")
    assert isinstance(loader, JsonFileLoader)


def test_create_file_loader_csv():
    """Test: creating a loader for CSV file"""
    loader = create_file_loader(".csv")
    assert isinstance(loader, CsvFileLoader)


def test_create_file_loader_yaml():
    """Test: creating a loader for YAML file"""
    loader = create_file_loader(".yaml")
    assert isinstance(loader, YamlFileLoader)


def test_create_file_loader_yml():
    """Test: creating a loader for YML file"""
    loader = create_file_loader(".yml")
    assert isinstance(loader, YamlFileLoader)


def test_create_file_loader_xlsx():
    """Test: creating a loader for Excel file"""
    loader = create_file_loader(".xlsx")
    assert isinstance(loader, ExcelFileLoader)


def test_create_file_loader_xml():
    """Test: creating a loader for XML file"""
    loader = create_file_loader(".xml")
    assert isinstance(loader, XmlFileLoader)


def test_create_file_loader_case_insensitive():
    """Test: case insensitivity of file extensions"""
    loader1 = create_file_loader(".JSON")
    loader2 = create_file_loader(".Json")
    assert isinstance(loader1, JsonFileLoader)
    assert isinstance(loader2, JsonFileLoader)


def test_create_file_loader_unsupported_format():
    """Test: handling unsupported file format"""
    with pytest.raises(ValueError, match="Unsupported file format: .txt"):
        create_file_loader(".txt")


def test_create_file_loader_empty_extension():
    """Test: handling empty file extension"""
    with pytest.raises(ValueError, match="Unsupported file format: "):
        create_file_loader("")
