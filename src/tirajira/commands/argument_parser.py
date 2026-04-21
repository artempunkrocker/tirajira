"""
Модуль для парсинга аргументов командной строки.
"""

import argparse
import sys

from .. import __version__
from .help_manager import display_help


class ArgumentParser:
    """Класс для парсинга аргументов командной строки."""

    def __init__(self) -> None:
        """Инициализирует парсер аргументов."""
        self.parser = argparse.ArgumentParser(
            description="TiraJira - инструмент для автоматизации создания задач в Jira",
            add_help=False,
        )
        self._add_arguments()

    def _add_arguments(self) -> None:
        """Добавляет аргументы к парсеру."""
        self.parser.add_argument("file_path", nargs="?", help="Путь к файлу с задачами")
        self.parser.add_argument(
            "--batch-size",
            "-b",
            type=int,
            default=10,
            help="Размер пакета для обработки задач (по умолчанию: 10)",
        )
        self.parser.add_argument(
            "--delay",
            "-d",
            type=float,
            default=1.0,
            help="Задержка между пакетами в секундах (по умолчанию: 1.0)",
        )
        self.parser.add_argument(
            "--stop-on-error",
            action="store_true",
            help="Прекратить обработку при возникновении ошибки",
        )
        self.parser.add_argument(
            "--verbose", action="store_true", help="Включить подробный режим вывода"
        )
        self.parser.add_argument(
            "--report",
            nargs="?",
            const=True,
            default=None,
            help="Сохранить отчет о выполнении (если указан без значения, "
            "имя файла генерируется автоматически)",
        )
        self.parser.add_argument(
            "--help", "-h", action="store_true", help="Показать помощь"
        )
        self.parser.add_argument(
            "--version", action="store_true", help="Показать версию"
        )

    def parse(self) -> argparse.Namespace:
        """
        Парсит аргументы командной строки.

        Returns:
            Namespace с распарсенными аргументами.
        """
        return self.parser.parse_args()

    def handle_special_args(self, args: argparse.Namespace) -> bool:
        """
        Обрабатывает специальные аргументы (--help, --version).

        Args:
            args: Распарсенные аргументы.

        Returns:
            True, если была выполнена специальная команда (help или version),
            иначе False.
        """
        if args.help or (len(sys.argv) == 1 and not args.file_path):
            display_help()
            return True

        if args.version:
            print(f"TiraJira version {__version__}")
            return True

        return False

    def validate_args(self, args: argparse.Namespace) -> bool:
        """
        Валидирует аргументы.

        Args:
            args: Распарсенные аргументы.

        Returns:
            True, если аргументы валидны, иначе False.
        """
        if not args.file_path:
            print("Ошибка: Не указан путь к файлу с задачами")
            display_help()
            return False
        return True
