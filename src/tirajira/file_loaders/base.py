"""
Базовый класс для загрузчиков файлов.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FileLoader(ABC):
    """Абстрактный класс для загрузки задач из файлов."""

    @abstractmethod
    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Загружает задачи из файла."""
        pass
