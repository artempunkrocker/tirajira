"""
Модуль для создания задач в Jira из файлов.
"""

import os
import os as os_module  # Для доступа к переменным окружения
import sys
from datetime import datetime
from typing import Optional

from .batch_processor import BatchProcessor
from .file_loaders import create_file_loader
from .jira_client import JiraClient
from .logger import get_logger
from .report_writers.factory import create_report_writer


class TaskCreator:
    """Класс для создания задач в Jira из файлов."""

    def __init__(
        self,
        jira_client: Optional[JiraClient] = None,
        batch_processor: Optional[BatchProcessor] = None,
        verbose: bool = False,
    ) -> None:
        """
        Инициализирует создателя задач.

        Args:
            jira_client: Клиент Jira. Если не указан, будет создан новый.
            batch_processor: Процессор пакетов. Если не указан, будет создан новый.
            verbose: Флаг подробного режима логирования.
        """
        self.logger = get_logger()
        self.logger.set_verbose(verbose)

        self.jira_client = jira_client or JiraClient(verbose=verbose)
        self.batch_processor = batch_processor or BatchProcessor(
            self.jira_client, verbose=verbose
        )

    def create_from_file(
        self,
        file_path: str,
        batch_size: int = 10,
        delay: float = 1.0,
        stop_on_error: bool = False,
        verbose: bool = False,
        report_file: Optional[str] = None,
    ) -> int:
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

        Returns:
            Количество успешно созданных задач.
        """
        self.logger.set_verbose(verbose)

        # Обновляем логгер в batch_processor
        if hasattr(self.batch_processor, "logger"):
            self.batch_processor.logger.set_verbose(verbose)

        self.logger.info(f"Запуск создания задач из файла: {file_path}")

        try:
            # Определяем тип файла по расширению
            _, file_extension = os.path.splitext(file_path)

            # Создаем подходящий загрузчик файлов
            loader = create_file_loader(file_extension)

            # Загружаем задачи из файла
            issues = loader.load_issues(file_path)
            self.logger.info(f"Загружено {len(issues)} задач из файла")

            # Обновляем параметры batch_processor
            self.batch_processor.batch_size = batch_size
            self.batch_processor.delay = delay
            self.batch_processor.stop_on_error = stop_on_error
            self.batch_processor.verbose = verbose

            # Пакетная отправка задач с передачей параметров
            successful_count, processing_details = self.batch_processor.process(
                issues,
                batch_size=batch_size,
                delay=delay,
                stop_on_error=stop_on_error,
                verbose=verbose,
            )

            self.logger.success(
                f"Успешно создано {successful_count} из {len(issues)} задач"
            )

            # Сохраняем отчет, если требуется
            if report_file is not None:
                self._save_report(
                    file_path,
                    processing_details,
                    report_file,
                    successful_count,
                    len(issues),
                )

            return successful_count

        except Exception as e:
            self.logger.error(f"Ошибка при создании задач: {e}")
            sys.exit(1)

    def _save_report(
        self,
        source_file: str,
        processing_details: list,
        report_file: Optional[str],
        successful_count: int,
        total_count: int,
    ) -> None:
        """
        Сохраняет отчет о выполнении.

        Args:
            source_file: Путь к исходному файлу с задачами.
            processing_details: Детали обработки задач.
            report_file: Путь к файлу отчета (None - не сохранять отчет,
                        True - автоматически сгенерировать имя файла,
                        str - использовать указанное имя файла).
            successful_count: Количество успешно созданных задач.
            total_count: Общее количество задач.
        """
        try:
            # Определяем путь к файлу отчета
            if report_file is True:
                # Автоматически генерируем имя файла
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = f"tirajira_report_{timestamp}.json"
            elif isinstance(report_file, str):
                # Используем указанное имя файла
                report_path = report_file
            else:
                # Не сохраняем отчет
                return

            # Определяем формат отчета по расширению файла
            _, file_extension = os.path.splitext(report_path)
            report_format = file_extension[1:].lower() if file_extension else "json"

            # Если расширение не указано или не поддерживается, используем JSON
            if report_format not in ["json", "yaml", "yml", "csv", "xlsx", "excel"]:
                report_format = "json"
                # Если пользователь указал имя файла без расширения, добавляем .json
                if isinstance(report_file, str) and not file_extension:
                    report_path += ".json"

            # Получаем URL сервера Jira из переменных окружения
            jira_server = os_module.getenv("JIRA_SERVER", "")

            # Формируем URL задач, если есть ключ задачи и сервер Jira
            if jira_server:
                for detail in processing_details:
                    if detail.get("issue_key"):
                        detail["issue_url"] = (
                            f"{jira_server.rstrip('/')}/browse/{detail['issue_key']}"
                        )

            # Подготавливаем данные отчета
            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "source_file": source_file,
                    "jira_server": jira_server,
                    "total_tasks": total_count,
                    "successful_tasks": successful_count,
                    "failed_tasks": total_count - successful_count,
                },
                "tasks": processing_details,
            }

            # Создаем писатель отчетов и записываем отчет
            writer = create_report_writer(report_format)
            writer.write_report(report_data, report_path)

            self.logger.info(f"Отчет сохранен в файл: {report_path}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении отчета: {e}")
