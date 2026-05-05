"""
Module for centralized logging with support for different levels of detail.
"""

import logging
import sys
from typing import Optional


class Logger:
    """Centralized logger with support for different output modes."""

    _instance: Optional["Logger"] = None
    _disable_console_output = False

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("tirajira")
            self.logger.setLevel(logging.DEBUG)

            if not Logger._disable_console_output:
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(logging.Formatter("%(message)s"))
                self.logger.addHandler(handler)

            self.verbose_mode = False

    @classmethod
    def disable_console_output(cls) -> None:
        cls._disable_console_output = True

        if cls._instance and hasattr(cls._instance, "logger"):
            cls._instance.logger.handlers.clear()

    @classmethod
    def enable_console_output(cls) -> None:
        cls._disable_console_output = False

        if cls._instance and hasattr(cls._instance, "logger"):
            cls._instance.logger.handlers.clear()
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(message)s"))
            cls._instance.logger.addHandler(handler)

    def set_verbose(self, verbose: bool) -> None:
        self.verbose_mode = verbose

        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def _add_emoji_prefix(self, message: str, emoji: str) -> str:
        return f"{emoji} {message}"

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(self._add_emoji_prefix(f"Error: {message}", "❌"))

    def debug(self, message: str) -> None:
        if self.verbose_mode:
            self.logger.debug(self._add_emoji_prefix(f"Debug: {message}", "🔍"))

    def progress(self, message: str) -> None:
        self.logger.info(self._add_emoji_prefix(message, "⏳"))

    def success(self, message: str) -> None:
        self.logger.info(self._add_emoji_prefix(message, "✅"))


def get_logger() -> Logger:
    return Logger()
