"""
Команда извлечения неудачных задач из отчета.
"""

import json
import os
from typing import Any, Dict, List, Optional

import yaml

from ..file_loaders import create_file_loader
from ..logger import get_logger
from ..report_writers.factory import create_report_writer
from .base import BaseCommand


class ExtractFailedCommand(BaseCommand):
    """Команда извлечения неудачных задач из отчета."""

    def execute(self):
        """Выполняет извлечение неудачных задач из отчета."""
        logger = get_logger()

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
            elif file_extension.lower() in [".yaml", ".yml"]:
                report_data = self._load_yaml_report(self.args.report_file)
                tasks = report_data.get("tasks", [])
            # Для других форматов используем существующий подход
            else:
                # Создаем подходящий загрузчик файлов
                loader = create_file_loader(file_extension)

                # Загружаем данные из отчета
                report_data = loader.load_issues(self.args.report_file)

                # Если это CSV/Excel отчет, то это список задач с префиксами
                tasks = report_data

            # Извлекаем неудачные задачи
            failed_tasks = self._extract_failed_tasks(tasks)

            # Проверяем, есть ли неудачные задачи
            if not failed_tasks:
                logger.info("Не найдено неудачных задач в отчете")
                return 0

            logger.info(f"Найдено {len(failed_tasks)} неудачных задач")

            # Определяем формат выходного файла по расширению
            _, output_extension = os.path.splitext(self.args.output_file)
            output_format = output_extension[1:].lower() if output_extension else "json"

            # Если расширение не поддерживается, используем JSON
            if output_format not in ["json", "yaml", "yml", "csv", "xlsx", "excel"]:
                output_format = "json"

            # Если пользователь указал имя файла без расширения, добавляем .json
            if not output_extension:
                self.args.output_file += ".json"

            # Создаем писатель отчетов и записываем извлеченные задачи
            writer = create_report_writer(output_format)

            # Для JSON/YAML форматов сохраняем как список задач
            # Для CSV/Excel форматов также сохраняем как список задач
            writer.write_report(failed_tasks, self.args.output_file)

            logger.success(
                f"Извлеченные задачи сохранены в файл: {self.args.output_file}"
            )

        except Exception as e:
            logger.error(f"Ошибка при извлечении неудачных задач: {e}")
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
