"""
Base class for file loaders.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FileLoader(ABC):
    """Abstract class for loading issues from files."""

    @abstractmethod
    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Loads issues from file."""
        pass
