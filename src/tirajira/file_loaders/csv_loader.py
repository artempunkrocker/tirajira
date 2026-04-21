"""
Загрузчик задач из CSV файлов.
"""

import csv
import os
from typing import Any, Dict, List

from ..utils.dot_notation_utils import convert_dot_notation_to_nested_dict
from .base import FileLoader


class CsvFileLoader(FileLoader):
    """Загрузчик задач из CSV файлов с поддержкой точечной нотации в заголовках."""

    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Загружает задачи из CSV файла с поддержкой точечной нотации в заголовках."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        try:
            issues = []
            with open(file_path, "r", encoding="utf-8") as f:
                # Определяем диалект CSV файла
                dialect = csv.Sniffer().sniff(f.read(1024))
                f.seek(0)

                reader = csv.DictReader(f, dialect=dialect)

                # Проверяем, что файл не пустой
                if reader.fieldnames is None:
                    raise ValueError("CSV файл пуст или поврежден")

                for row in reader:
                    # Пропускаем пустые строки
                    if not any(row.values()):
                        continue

                    # Фильтруем пустые значения
                    filtered_row = {
                        k: v for k, v in row.items() if v is not None and v != ""
                    }

                    # Преобразуем плоский словарь с точечной нотацией в вложенный
                    nested_dict = convert_dot_notation_to_nested_dict(filtered_row)

                    issues.append(nested_dict)

            return issues
        except csv.Error as e:
            raise ValueError(f"Ошибка парсинга CSV файла: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}") from e
