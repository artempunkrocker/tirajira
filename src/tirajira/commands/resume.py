"""
Команда продолжения выполнения из отчета.
"""

import json
import os
from typing import Any, Dict, List, Optional

import yaml

from ..batch_processor import BatchProcessor
from ..file_loaders import create_file_loader
from ..jira_client import JiraClient
from ..logger import get_logger
from ..task_creator import TaskCreator
from .base import BaseCommand


class ResumeCommand(BaseCommand):
    """Команда продолжения выполнения из отчета."""

    def execute(self):
        """Выполняет продолжение выполнения из отчета."""
        logger = get_logger()
        logger.set_verbose(self.args.verbose)

        # Проверяем существование файла отчета
        if not os.path.exists(self.args.report_file):
            logger.error(f"Файл отчета {self.args.report_file} не найден")
            return 1

        try:
            # Определяем тип файла отчета по расширению
            _, file_extension = os.path.splitext(self.args.report_file)

            # Для JSON и YAML файлов отчетов используем специальную логику
            if file_extension.lower() in [".json"]:
                report_data = self._load_json_report(self.args.report_file)
                tasks = report_data.get("tasks", [])
                source_file = report_data.get("metadata", {}).get("source_file", "")
            elif file_extension.lower() in [".yaml", ".yml"]:
                report_data = self._load_yaml_report(self.args.report_file)
                tasks = report_data.get("tasks", [])
                source_file = report_data.get("metadata", {}).get("source_file", "")
            # Для других форматов используем существующий подход
            else:
                # Создаем подходящий загрузчик файлов
                loader = create_file_loader(file_extension)

                # Загружаем данные из отчета
                report_data = loader.load_issues(self.args.report_file)

                # Если это CSV/Excel отчет, то это список задач с префиксами
                tasks = report_data
                # Для CSV/Excel отчетов мы не можем получить source_file,
                # поэтому используем путь к отчету как источник
                source_file = self.args.report_file

            # Извлекаем неудачные задачи
            failed_tasks = self._extract_failed_tasks(tasks)

            # Проверяем, есть ли неудачные задачи
            if not failed_tasks:
                logger.info(
                    "Не найдено неудачных задач в отчете для повторной обработки"
                )
                return 0

            logger.info(
                f"Найдено {len(failed_tasks)} неудачных задач для повторной обработки"
            )

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

            # Обновляем параметры batch_processor
            batch_processor.batch_size = self.args.batch_size
            batch_processor.delay = self.args.delay
            batch_processor.stop_on_error = self.args.stop_on_error
            batch_processor.verbose = self.args.verbose

            # Пакетная отправка неудачных задач
            successful_count, processing_details = batch_processor.process(
                failed_tasks,
                batch_size=self.args.batch_size,
                delay=self.args.delay,
                stop_on_error=self.args.stop_on_error,
                verbose=self.args.verbose,
            )

            logger.success(
                f"Успешно обработано {successful_count} из {len(failed_tasks)} задач"
            )

            # Сохраняем отчет, если требуется
            if self.args.report is not None:
                # Используем source_file из метаданных отчета для логирования
                task_creator._save_report(
                    source_file,
                    processing_details,
                    self.args.report,
                    successful_count,
                    len(failed_tasks),
                )

        except Exception as e:
            logger.error(f"Ошибка при продолжении выполнения: {e}")
            return 1

        return 0

    def _load_report(self, file_path: str) -> Dict[str, Any]:
        """
        Загружает отчет из файла.

        Args:
            file_path: Путь к файлу отчета

        Returns:
            Словарь с данными отчета
        """
        _, file_extension = os.path.splitext(file_path)

        if file_extension.lower() in [".json"]:
            return self._load_json_report(file_path)
        elif file_extension.lower() in [".yaml", ".yml"]:
            return self._load_yaml_report(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла отчета: {file_extension}")

    def _load_json_report(self, file_path: str) -> Dict[str, Any]:
        """
        Загружает отчет из JSON файла.

        Args:
            file_path: Путь к JSON файлу отчета

        Returns:
            Словарь с данными отчета
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)

            # Проверяем, что данные имеют правильный формат
            if not isinstance(report_data, dict):
                raise ValueError("JSON файл отчета должен содержать объект")

            return report_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON файла отчета: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла отчета: {str(e)}") from e

    def _load_yaml_report(self, file_path: str) -> Dict[str, Any]:
        """
        Загружает отчет из YAML файла.

        Args:
            file_path: Путь к YAML файлу отчета

        Returns:
            Словарь с данными отчета
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                report_data = yaml.safe_load(f)

            # Проверяем, что данные имеют правильный формат
            if not isinstance(report_data, dict):
                raise ValueError("YAML файл отчета должен содержать объект")

            return report_data
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка парсинга YAML файла отчета: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла отчета: {str(e)}") from e

    def _extract_from_json_yaml_report(
        self, task: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Извлекает задачу из JSON/YAML отчета."""
        status = task.get("status", "").lower()
        if status == "failure":
            # Извлекаем оригинальные данные задачи
            original_data = task.get("issue_data", {})
            if original_data:
                return original_data
            else:
                # Если issue_data нет, сохраняем всю задачу
                # без служебных полей
                cleaned_task = {
                    key: value
                    for key, value in task.items()
                    if key not in ["status", "error_message", "processed_at"]
                }
                return cleaned_task
        return None

    def _extract_from_csv_excel_report(
        self, task: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Извлекает задачу из CSV/Excel отчета."""
        status = task.get("tasks.status", "").lower()
        if status == "failure":
            # Извлекаем оригинальные данные задачи (поля без префикса tasks.)
            original_data = {}
            for key, value in task.items():
                if key.startswith("tasks.") and not key.startswith("tasks.status"):
                    original_key = key.replace("tasks.", "", 1)
                    original_data[original_key] = value
            if original_data:
                return original_data
        return None

    def _extract_failed_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Извлекает неудачные задачи из списка задач.

        Args:
            tasks: Список задач из отчета

        Returns:
            Список неудачных задач в оригинальном формате
        """
        failed_tasks = []

        for task in tasks:
            # Для JSON/YAML отчетов проверяем поле status
            if isinstance(task, dict):
                # Проверяем формат JSON/YAML отчета
                if "status" in task:
                    extracted_task = self._extract_from_json_yaml_report(task)
                    if extracted_task:
                        failed_tasks.append(extracted_task)
                # Для CSV/Excel отчетов проверяем поле с префиксом tasks.status
                elif "tasks.status" in task:
                    extracted_task = self._extract_from_csv_excel_report(task)
                    if extracted_task:
                        failed_tasks.append(extracted_task)

        return failed_tasks
