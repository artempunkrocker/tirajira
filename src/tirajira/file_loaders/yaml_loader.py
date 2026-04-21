"""
Загрузчик задач из YAML файлов.
"""

import os
from typing import Any, Dict, List

import yaml

from .base import FileLoader


class YamlFileLoader(FileLoader):
    """Загрузчик задач из YAML файлов."""

    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Загружает задачи из YAML файла."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                issues = yaml.safe_load(f)

            # Проверяем, что данные имеют правильный формат
            if not isinstance(issues, list):
                raise ValueError("YAML файл должен содержать массив задач")

            return issues
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка парсинга YAML файла: {str(e)}") from e
        except ValueError:
            # Перебрасываем ValueError без оборачивания
            raise
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}") from e
