"""
Главный скрипт для автоматизации создания задач в Jira.
Поддерживает создание задач по списку из файла (JSON/YAML/CSV/Excel).
"""

import sys
from typing import Optional

from .batch_processor import BatchProcessor

# Импортируем необходимые классы для совместимости с тестами
from .commands.cli import main as cli_main
from .jira_client import JiraClient
from .logger import get_logger
from .task_creator import TaskCreator


def create_tasks_from_file(
    file_path: str,
    batch_size: int = 10,
    delay: float = 1.0,
    stop_on_error: bool = False,
    verbose: bool = False,
    report_file: Optional[str] = None,
) -> None:
    """
    Создание задач на основе списка из файла.

    Args:
        file_path: Путь к файлу с задачами.
        batch_size: Размер пакета для обработки задач.
        delay: Задержка между пакетами в секундах.
        stop_on_error: Прекратить обработку при возникновении ошибки.
        verbose: Флаг подробного режима логирования.
        report_file: Путь к файлу отчета (None - не сохранять отчет,
                    True - автоматически сгенерировать имя файла,
                    str - использовать указанное имя файла).
    """
    # Инициализация логгера
    logger = get_logger()
    logger.set_verbose(verbose)

    try:
        # Инициализация клиента Jira
        jira_client = JiraClient(verbose=verbose)

        # Инициализация процессора пакетов
        batch_processor = BatchProcessor(
            jira_client,
            batch_size=batch_size,
            delay=delay,
            stop_on_error=stop_on_error,
            verbose=verbose,
        )

        # Инициализация создателя задач
        task_creator = TaskCreator(
            jira_client=jira_client, batch_processor=batch_processor, verbose=verbose
        )

        # Создаем задачи
        task_creator.create_from_file(
            file_path=file_path,
            batch_size=batch_size,
            delay=delay,
            stop_on_error=stop_on_error,
            verbose=verbose,
            report_file=report_file,
        )

    except Exception as e:
        logger.error(f"Ошибка при создании задач: {e}")
        sys.exit(1)


def main() -> None:
    """Основная точка входа в приложение."""
    # Используем новый CLI интерфейс
    cli_main()


if __name__ == "__main__":
    main()
    sys.exit(0)  # Выходим с кодом 0 если всё прошло успешно
