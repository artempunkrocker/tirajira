"""
Загрузчик задач из JSON файлов.
"""

import json
import os
from typing import Any, Dict, List

from .base import FileLoader


class JsonFileLoader(FileLoader):
    """Загрузчик задач из JSON файлов."""

    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Загружает задачи из JSON файла."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                issues = json.load(f)

            # Проверяем, что данные имеют правильный формат
            if not isinstance(issues, list):
                raise ValueError("JSON файл должен содержать массив задач")

            return issues
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON файла: {str(e)}") from e
        except ValueError:
            # Перебрасываем ValueError без оборачивания
            raise
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}") from e
