"""
Factory for creating file loaders.
"""

from typing import Dict, Type

from .base import FileLoader
from .csv_loader import CsvFileLoader
from .excel_loader import ExcelFileLoader
from .json_loader import JsonFileLoader
from .xml_loader import XmlFileLoader
from .yaml_loader import YamlFileLoader


def create_file_loader(file_extension: str) -> FileLoader:
    """Creates file loader depending on file extension."""
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
        raise ValueError(f"Unsupported file format: {file_extension}")

    return loader_class()
