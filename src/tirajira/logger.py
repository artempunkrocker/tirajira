"""
Модуль для централизованного логирования с поддержкой разных уровней детализации.
"""

import logging
import sys
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    """Уровни логирования."""

    NORMAL = "normal"
    VERBOSE = "verbose"


class Logger:
    """Централизованный логгер с поддержкой разных режимов вывода."""

    _instance: Optional["Logger"] = None
    _initialized: bool = False

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self.logger = logging.getLogger("tirajira")
            self.logger.setLevel(logging.DEBUG)

            # Создаем обработчик для вывода в консоль
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

            self.verbose_mode = False
            self._initialized = True

    def set_verbose(self, verbose: bool) -> None:
        """Установка режима подробного логирования."""
        self.verbose_mode = verbose

        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def info(self, message: str) -> None:
        """Вывод информационного сообщения."""
        self.logger.info(message)

    def error(self, message: str) -> None:
        """Вывод сообщения об ошибке."""
        self.logger.error(f"❌ Ошибка: {message}")

    def debug(self, message: str) -> None:
        """Вывод отладочного сообщения (только в verbose режиме)."""
        if self.verbose_mode:
            self.logger.debug(f"🔍 Debug: {message}")

    def progress(self, message: str) -> None:
        """Вывод сообщения о прогрессе."""
        self.logger.info(f"⏳ {message}")

    def success(self, message: str) -> None:
        """Вывод сообщения об успехе."""
        self.logger.info(f"✅ {message}")


def get_logger() -> Logger:
    """Получение экземпляра логгера (Singleton)."""
    return Logger()
