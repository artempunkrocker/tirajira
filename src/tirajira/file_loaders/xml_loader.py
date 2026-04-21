"""
Загрузчик задач из XML файлов.
"""

import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

from ..utils.dot_notation_utils import convert_dot_notation_to_nested_dict
from .base import FileLoader


def _get_element_text_with_children(element: Element) -> str:
    """
    Получает текстовое содержимое элемента со всеми вложенными элементами.

    Args:
        element: Элемент XML

    Returns:
        Текстовое содержимое элемента
    """
    # Начинаем с текста до первого дочернего элемента
    text_parts = [element.text or ""]

    # Добавляем текст из всех дочерних элементов
    for child in element:
        # Добавляем текст дочернего элемента
        text_parts.append(child.text or "")
        # Добавляем текст после дочернего элемента
        text_parts.append(child.tail or "")

    # Объединяем все части и убираем лишние пробелы
    return "".join(text_parts).strip()


class XmlFileLoader(FileLoader):
    """Загрузчик задач из XML файлов."""

    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Загружает задачи из XML файла."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        try:
            # Парсим XML файл
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Проверяем, что корневой элемент - 'issues'
            if root.tag != "issues":
                raise ValueError("XML файл должен содержать корневой элемент 'issues'")

            issues = []
            # Обрабатываем каждый элемент 'issue' в корневом элементе
            for issue_element in root.findall("issue"):
                issue_dict = self._element_to_dict(issue_element)
                issues.append(issue_dict)

            return issues
        except ET.ParseError as e:
            raise ValueError(f"Ошибка парсинга XML файла: {str(e)}") from e
        except ValueError:
            # Перебрасываем ValueError без оборачивания
            raise
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}") from e

    def _element_to_dict(self, element: Element) -> Dict[Any, Any]:
        """
        Преобразует XML элемент в словарь.

        Args:
            element: Элемент XML для преобразования

        Returns:
            Словарь, представляющий структуру XML элемента
        """
        # Если у элемента нет дочерних элементов и атрибутов, возвращаем его текст
        if len(element) == 0 and not element.attrib:
            text = element.text.strip() if element.text else ""
            return text

        # Если у элемента есть дочерние элементы, но нет атрибутов,
        # и мы хотим получить текст со всеми вложенными элементами
        if len(element) > 0 and not element.attrib:
            # Проверяем, содержит ли элемент текст со смешанным содержимым
            if element.text or any(child.tail for child in element):
                text = _get_element_text_with_children(element)
                return text

        result = {}

        # Обрабатываем атрибуты элемента
        self._process_attributes(element, result)

        # Обрабатываем дочерние элементы
        children_dict = self._process_children(element)

        # Объединяем children_dict с result
        self._merge_dicts(result, children_dict)

        # Постобработка для специальных случаев
        self._post_process_result(result)

        return result

    def _process_attributes(self, element: Element, result: Dict[Any, Any]) -> None:
        """
        Обрабатывает атрибуты XML элемента.

        Args:
            element: Элемент XML для обработки атрибутов
            result: Словарь для сохранения результата
        """
        for key, value in element.attrib.items():
            # Если ключ использует точечную нотацию, парсим его правильно
            if "." in key:
                # Создаем временный словарь с одним ключом и преобразуем его
                temp_dict = {key: value}
                nested_dict = convert_dot_notation_to_nested_dict(temp_dict)
                # Объединяем с результатом
                self._merge_dicts(result, nested_dict)
            else:
                # Для специальных атрибутов создаем нужную структуру
                if key == "email":
                    result["emailAddress"] = value
                elif key == "name":
                    result["name"] = value
                elif key == "key":
                    result["key"] = value
                else:
                    result[key] = value

    def _process_children(self, element: Element) -> Dict[Any, Any]:
        """
        Обрабатывает дочерние элементы XML элемента.

        Args:
            element: Элемент XML для обработки дочерних элементов

        Returns:
            Словарь с обработанными дочерними элементами
        """
        children_dict = {}
        # Группируем дочерние элементы по тегу
        children_by_tag = {}
        for child in element:
            if child.tag not in children_by_tag:
                children_by_tag[child.tag] = []
            children_by_tag[child.tag].append(child)

        # Обрабатываем каждую группу дочерних элементов
        for tag, children in children_by_tag.items():
            if tag == "customfield":
                # Специальная обработка для customfield
                self._process_customfields(children, children_dict)
                continue

            if len(children) == 1:
                # Один элемент - обрабатываем его как обычный элемент
                child_dict = self._process_child_element(children[0])
                self._add_to_children_dict(tag, child_dict, children_dict)
            else:
                # Несколько элементов с одинаковым тегом - создаем список
                child_list = []
                for child in children:
                    child_dict = self._process_child_element(child)
                    child_list.append(child_dict)

                self._add_to_children_dict(tag, child_list, children_dict)

        return children_dict

    def _process_customfields(
        self, children: List[Element], children_dict: Dict[Any, Any]
    ) -> None:
        """
        Специальная обработка для customfield элементов.

        Args:
            children: Список дочерних элементов типа customfield
            children_dict: Словарь для сохранения результата
        """
        for child in children:
            # Для customfield используем id в качестве ключа,
            # а текст в качестве значения
            id_attr = child.get("id")
            if id_attr:
                # Формируем правильный ключ для customfield
                if not id_attr.startswith("customfield_"):
                    key = f"customfield_{id_attr}"
                else:
                    key = id_attr
                # Получаем текстовое содержимое элемента
                text = child.text.strip() if child.text else ""
                children_dict[key] = text

    def _process_child_element(self, child: Element) -> Any:
        """
        Обрабатывает один дочерний элемент.

        Args:
            child: Дочерний элемент для обработки

        Returns:
            Результат обработки дочернего элемента
        """
        # Если у дочернего элемента есть дочерние элементы или атрибуты,
        # рекурсивно преобразуем его в словарь
        if len(child) > 0 or child.attrib:
            # Проверяем, содержит ли элемент текст со смешанным содержимым
            if child.text or any(ch.tail for ch in child):
                # Используем _get_element_text_with_children для получения
                # текста со всеми вложенными элементами
                return _get_element_text_with_children(child)
            else:
                return self._element_to_dict(child)
        else:
            # Если дочерний элемент является текстовым узлом
            return child.text.strip() if child.text else ""

    def _add_to_children_dict(
        self, tag: str, value: Any, children_dict: Dict[Any, Any]
    ) -> None:
        """
        Добавляет значение в словарь дочерних элементов с учетом точечной нотации.

        Args:
            tag: Тег элемента
            value: Значение для добавления
            children_dict: Словарь дочерних элементов
        """
        # Если ключ использует точечную нотацию, парсим его правильно
        if "." in tag:
            # Создаем временный словарь с одним ключом и преобразуем его
            temp_dict = {tag: value}
            nested_dict = convert_dot_notation_to_nested_dict(temp_dict)
            # Объединяем с children_dict
            self._merge_dicts(children_dict, nested_dict)
        else:
            children_dict[tag] = value

    def _post_process_result(self, result: Dict[Any, Any]) -> None:
        """
        Постобработка результата для специальных случаев.

        Args:
            result: Словарь результата для постобработки
        """
        # Обработка labels
        if (
            "labels" in result
            and isinstance(result["labels"], dict)
            and "label" in result["labels"]
        ):
            label_data = result["labels"]["label"]
            if isinstance(label_data, list):
                result["labels"] = label_data
            else:
                result["labels"] = [label_data]

        # Обработка attachments
        if (
            "attachments" in result
            and isinstance(result["attachments"], dict)
            and "attachment" in result["attachments"]
        ):
            attachment_data = result["attachments"]["attachment"]
            if isinstance(attachment_data, list):
                result["attachments"] = attachment_data
            else:
                result["attachments"] = [attachment_data]

        # Специальная обработка для customfields - выносим все customfield
        # на уровень выше
        if "customfields" in result:
            customfields = result.pop("customfields")
            if isinstance(customfields, dict):
                for key, value in customfields.items():
                    if key.startswith("customfield_"):
                        result[key] = value

    def _merge_dicts(self, target: Dict[Any, Any], source: Dict[Any, Any]) -> None:
        """
        Рекурсивно объединяет два словаря.

        Args:
            target: Целевой словарь для объединения
            source: Источник данных для объединения
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                # Если оба значения являются словарями, рекурсивно объединяем их
                self._merge_dicts(target[key], value)
            elif key in target and isinstance(target[key], list):
                # Если значение в target уже является списком, добавляем к нему
                target[key].append(value)
            elif key in target:
                # Если ключ уже существует, преобразуем в список
                target[key] = [target[key], value]
            else:
                # Если ключ не существует, просто добавляем его
                target[key] = value
