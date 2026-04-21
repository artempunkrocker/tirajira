"""
Тесты для утилит работы с точечной нотацией.
"""

from tirajira.utils.dot_notation_utils import convert_dot_notation_to_nested_dict


def test_convert_dot_notation_to_nested_dict_simple():
    """Тест: преобразование простого словаря без точечной нотации."""
    flat_dict = {"key": "value"}
    expected = {"key": "value"}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_single_level():
    """Тест: преобразование словаря с одиночной точечной нотацией."""
    flat_dict = {"project.key": "PROJ"}
    expected = {"project": {"key": "PROJ"}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_multiple_levels():
    """Тест: преобразование словаря с многоуровневой точечной нотацией."""
    flat_dict = {"project.key": "PROJ", "issuetype.name": "Task"}
    expected = {"project": {"key": "PROJ"}, "issuetype": {"name": "Task"}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_deep_nesting():
    """Тест: преобразование словаря с глубокой вложенностью."""
    flat_dict = {"project.category.type.name": "Software"}
    expected = {"project": {"category": {"type": {"name": "Software"}}}}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_mixed_keys():
    """Тест: преобразование словаря с смешанными ключами (с точками и без)."""
    flat_dict = {
        "summary": "Test task",
        "project.key": "PROJ",
        "issuetype.name": "Task",
    }
    expected = {
        "summary": "Test task",
        "project": {"key": "PROJ"},
        "issuetype": {"name": "Task"},
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_empty_dict():
    """Тест: преобразование пустого словаря."""
    flat_dict = {}
    expected = {}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_keys_with_numbers():
    """Тест: преобразование словаря с ключами, содержащими числа."""
    flat_dict = {"customfield_10001": "Value"}
    expected = {"customfield_10001": "Value"}
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected


def test_convert_dot_notation_to_nested_dict_complex_example():
    """Тест: преобразование словаря со сложным примером из документации."""
    flat_dict = {
        "project.key": "PROJ",
        "issuetype.name": "Task",
        "customfield_10001": "Бизнес-ценность: Высокая",
        "assignee.emailAddress": "developer@example.com",
    }
    expected = {
        "project": {"key": "PROJ"},
        "issuetype": {"name": "Task"},
        "customfield_10001": "Бизнес-ценность: Высокая",
        "assignee": {"emailAddress": "developer@example.com"},
    }
    result = convert_dot_notation_to_nested_dict(flat_dict)
    assert result == expected
