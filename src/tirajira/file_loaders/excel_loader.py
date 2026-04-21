"""
Загрузчик задач из Excel файлов.
"""

import os
from typing import Any, Dict, List, Tuple

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from ..utils.dot_notation_utils import convert_dot_notation_to_nested_dict
from .base import FileLoader


class ExcelFileLoader(FileLoader):
    """Загрузчик задач из Excel файлов с поддержкой точечной нотации в заголовках."""

    def _get_headers(self, sheet) -> List[str]:
        """Получает заголовки из первой строки листа."""
        headers = []
        for col in range(1, sheet.max_column + 1):
            header = sheet.cell(row=1, column=col).value
            if header is not None:
                headers.append(str(header))
            else:
                headers.append(f"column_{col}")
        return headers

    def _read_row_data(
        self, sheet, row: int, headers: List[str]
    ) -> Tuple[Dict[str, str], bool]:
        """Читает данные из строки листа."""
        row_data = {}
        has_data = False

        for col_idx, header in enumerate(headers, 1):
            cell_value = sheet.cell(row=row, column=col_idx).value
            if cell_value is not None:
                row_data[header] = str(cell_value)
                has_data = True

        return row_data, has_data

    def _process_row_data(self, row_data: Dict[str, str]) -> Dict[Any, Any]:
        """Обрабатывает данные строки."""
        # Фильтруем пустые значения
        filtered_row = {k: v for k, v in row_data.items() if v is not None and v != ""}

        # Преобразуем плоский словарь с точечной нотацией в вложенный
        nested_dict = convert_dot_notation_to_nested_dict(filtered_row)

        return nested_dict

    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Загружает задачи из Excel файла с поддержкой точечной нотации
        в заголовках."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        try:
            # Загружаем рабочую книгу
            workbook = load_workbook(file_path, read_only=True, data_only=True)

            # Работаем с активным листом
            sheet = workbook.active

            # Проверяем, что лист не пустой
            if sheet.max_row == 0 or sheet.max_column == 0:
                raise ValueError("Excel файл пуст или поврежден")

            # Получаем заголовки из первой строки
            headers = self._get_headers(sheet)

            # Проверяем, что есть заголовки
            if not headers:
                raise ValueError("Excel файл не содержит заголовков")

            issues = []

            # Читаем данные из остальных строк
            for row in range(2, sheet.max_row + 1):
                row_data, has_data = self._read_row_data(sheet, row, headers)

                # Пропускаем пустые строки
                if not has_data:
                    continue

                # Обрабатываем данные строки
                nested_dict = self._process_row_data(row_data)

                issues.append(nested_dict)

            workbook.close()
            return issues

        except InvalidFileException as e:
            raise ValueError(f"Ошибка парсинга Excel файла: {str(e)}") from e
        except ValueError:
            # Перебрасываем ValueError без оборачивания
            raise
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}") from e
