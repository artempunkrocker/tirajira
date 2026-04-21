"""
Писатель отчетов в формате XML.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict

from .base import ReportWriter


class XmlReportWriter(ReportWriter):
    """Писатель отчетов в формате XML."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Записывает отчет в XML файл.

        Args:
            report_data: Данные отчета для записи
            file_path: Путь к файлу отчета
        """
        # Создаем корневой элемент
        root = ET.Element("report")

        # Добавляем метаданные
        metadata_element = ET.SubElement(root, "metadata")
        self._dict_to_elements(metadata_element, report_data.get("metadata", {}))

        # Добавляем задачи
        tasks_element = ET.SubElement(root, "tasks")
        for task in report_data.get("tasks", []):
            task_element = ET.SubElement(tasks_element, "task")
            self._dict_to_elements(task_element, task)

        # Создаем дерево XML и записываем в файл
        tree = ET.ElementTree(root)

        # Форматируем XML для лучшей читаемости
        self._indent(root)

        # Записываем в файл
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def _dict_to_elements(self, parent: ET.Element, data: Dict[str, Any]) -> None:
        """
        Преобразует словарь в элементы XML.

        Args:
            parent: Родительский элемент XML
            data: Словарь для преобразования
        """
        for key, value in data.items():
            if isinstance(value, dict):
                # Для вложенных словарей создаем отдельный элемент
                element = ET.SubElement(parent, key)
                self._dict_to_elements(element, value)
            elif isinstance(value, list):
                # Для списков создаем отдельный элемент для каждого элемента
                list_element = ET.SubElement(parent, key)
                for item in value:
                    if isinstance(item, dict):
                        item_element = ET.SubElement(list_element, "item")
                        self._dict_to_elements(item_element, item)
                    else:
                        item_element = ET.SubElement(list_element, "item")
                        item_element.text = str(item)
            else:
                # Для простых значений создаем элемент с текстом
                element = ET.SubElement(parent, key)
                element.text = str(value) if value is not None else ""

    def _indent(self, elem: ET.Element, level: int = 0) -> None:
        """
        Добавляет отступы для форматирования XML.

        Args:
            elem: Элемент XML для форматирования
            level: Уровень отступа
        """
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
