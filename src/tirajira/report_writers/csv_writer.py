"""
Писатель отчетов в формате CSV.
"""

import csv
import json
from collections.abc import MutableMapping
from typing import Any, Dict

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
            # Для списков преобразуем каждый элемент в отдельное поле
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    # Рекурсивно преобразуем словари в списке
                    items.extend(
                        flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    )
                else:
                    # Для простых значений в списке просто добавляем их
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


class CsvReportWriter(ReportWriter):
    """Писатель отчетов в формате CSV."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Записывает отчет в CSV файл.

        Args:
            report_data: Данные отчета для записи
            file_path: Путь к файлу отчета
        """
        # Преобразуем вложенные структуры в плоские
        flattened_data = flatten_dict(report_data)

        # Преобразуем все значения в строки для CSV
        csv_data = {}
        for key, value in flattened_data.items():
            if isinstance(value, (dict, list)):
                # Преобразуем сложные объекты в JSON строки
                csv_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                csv_data[key] = str(value) if value is not None else ""

        # Записываем в CSV файл
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Записываем заголовки
            writer.writerow(csv_data.keys())
            # Записываем значения
            writer.writerow(csv_data.values())
