"""
Фабрика для создания загрузчиков файлов.
"""

from typing import Dict, Type

from .base import FileLoader
from .csv_loader import CsvFileLoader
from .excel_loader import ExcelFileLoader
from .json_loader import JsonFileLoader
from .xml_loader import XmlFileLoader
from .yaml_loader import YamlFileLoader


def create_file_loader(file_extension: str) -> FileLoader:
    """Создает загрузчик файлов в зависимости от расширения файла."""
    loaders: Dict[str, Type[FileLoader]] = {
        ".json": JsonFileLoader,
        ".csv": CsvFileLoader,
        ".yaml": YamlFileLoader,
        ".yml": YamlFileLoader,
        ".xlsx": ExcelFileLoader,
        ".xml": XmlFileLoader,
    }

    loader_class = loaders.get(file_extension.lower())
    if loader_class is None:
        raise ValueError(f"Не поддерживаемый формат файла: {file_extension}")

    return loader_class()
