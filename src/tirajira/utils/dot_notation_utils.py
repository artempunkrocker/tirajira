"""
Утилиты для работы с точечной нотацией в ключах словарей.
"""

from typing import Any, Dict


def convert_dot_notation_to_nested_dict(flat_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Преобразует плоский словарь с точечной нотацией в вложенный словарь.

    Args:
        flat_dict: Плоский словарь с точечной нотацией в ключах

    Returns:
        Вложенный словарь

    Example:
        >>> convert_dot_notation_to_nested_dict({'project.key': 'PROJ',
                                                 'issuetype.name': 'Task'})
        {'project': {'key': 'PROJ'}, 'issuetype': {'name': 'Task'}}
    """
    nested_dict: Dict[str, Any] = {}

    for key, value in flat_dict.items():
        if "." in key:
            # Разбиваем ключ по точкам
            parts = key.split(".")
            current_dict = nested_dict

            # Создаем вложенные словари для всех частей, кроме последней
            for part in parts[:-1]:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

            # Устанавливаем значение для последней части
            current_dict[parts[-1]] = value
        else:
            # Ключ без точек добавляем напрямую
            nested_dict[key] = value

    return nested_dict
