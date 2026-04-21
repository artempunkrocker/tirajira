"""
Команда импорта задач из файла.
"""

import sys

from ..batch_processor import BatchProcessor
from ..jira_client import JiraClient
from ..logger import get_logger
from ..task_creator import TaskCreator
from .base import BaseCommand


class ImportCommand(BaseCommand):
    """Команда импорта задач из файла."""

    def execute(self):
        """Выполняет импорт задач из файла."""
        logger = get_logger()
        logger.set_verbose(self.args.verbose)

        try:
            # Инициализация клиента Jira
            jira_client = JiraClient(verbose=self.args.verbose)

            # Инициализация процессора пакетов
            batch_processor = BatchProcessor(
                jira_client,
                batch_size=self.args.batch_size,
                delay=self.args.delay,
                stop_on_error=self.args.stop_on_error,
                verbose=self.args.verbose,
            )

            # Инициализация создателя задач
            task_creator = TaskCreator(
                jira_client=jira_client,
                batch_processor=batch_processor,
                verbose=self.args.verbose,
            )

            # Создаем задачи с указанными параметрами
            task_creator.create_from_file(
                file_path=self.args.file,
                batch_size=self.args.batch_size,
                delay=self.args.delay,
                stop_on_error=self.args.stop_on_error,
                verbose=self.args.verbose,
                report_file=self.args.report,
            )

        except Exception as e:
            logger.error(f"Ошибка при импорте задач: {e}")
            sys.exit(1)
