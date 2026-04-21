"""
Писатель отчетов в формате Excel.
"""

import json
from collections.abc import MutableMapping
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from .base import ReportWriter


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """
    Преобразует вложенный словарь в плоский соединием ключей через точку.

    Args:
        d: Вложенный словарь для преобразования
        parent_key: Родительский ключ (для рекурсивных вызовов)
        sep: Разделитель для объединения ключей

    Returns:
        Плоский словарь с ключами, соединенными через точку
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Преобразуем список в JSON строку
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        else:
            items.append((new_key, v))
    return dict(items)


class ExcelReportWriter(ReportWriter):
    """Писатель отчетов в формате Excel."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Записывает отчет в Excel файл с двумя листами: Metadata и Tasks.

        Args:
            report_data: Данные отчета для записи
            file_path: Путь к файлу отчета
        """
        wb = Workbook()

        # Удаляем стандартный лист, созданный по умолчанию
        wb.remove(wb.active)

        # Создаем лист для метаданных
        metadata_sheet = wb.create_sheet("Metadata")
        self._write_metadata_sheet(metadata_sheet, report_data.get("metadata", {}))

        # Создаем лист для задач
        tasks_sheet = wb.create_sheet("Tasks")
        self._write_tasks_sheet(tasks_sheet, report_data.get("tasks", []))

        # Сохраняем файл
        wb.save(file_path)

    def _write_metadata_sheet(self, sheet, metadata: Dict[str, Any]) -> None:
        """
        Записывает метаданные в лист в формате ключ-значение.

        Args:
            sheet: Лист Excel для записи
            metadata: Метаданные для записи
        """
        if not metadata:
            return

        row = 1
        for key, value in metadata.items():
            sheet[f"A{row}"] = key
            sheet[f"B{row}"] = str(value) if value is not None else ""
            row += 1

        # Автоматически подстраиваем ширину колонок
        sheet.column_dimensions["A"].width = 25
        sheet.column_dimensions["B"].width = 50

    def _write_tasks_sheet(self, sheet, tasks: List[Dict[str, Any]]) -> None:
        """
        Записывает задачи в табличном формате.

        Args:
            sheet: Лист Excel для записи
            tasks: Список задач для записи
        """
        if not tasks:
            return

        # Преобразуем все задачи в плоский формат
        flattened_tasks = [flatten_dict(task) for task in tasks]

        # Собираем все уникальные ключи для заголовков
        all_keys = set()
        for task in flattened_tasks:
            all_keys.update(task.keys())
        headers = sorted(all_keys)

        # Записываем заголовки
        for col_idx, header in enumerate(headers, 1):
            sheet[f"{get_column_letter(col_idx)}1"] = header

        # Записываем данные задач
        for row_idx, task in enumerate(flattened_tasks, 2):
            for col_idx, header in enumerate(headers, 1):
                value = task.get(header, "")
                sheet[f"{get_column_letter(col_idx)}{row_idx}"] = (
                    str(value) if value is not None else ""
                )

        # Автоматически подстраиваем ширину колонок
        for col_idx, header in enumerate(headers, 1):
            column_width = max(len(header), 15)  # Минимальная ширина 15
            sheet.column_dimensions[get_column_letter(col_idx)].width = min(
                column_width, 50
            )
