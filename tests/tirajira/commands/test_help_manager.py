"""
Тесты для менеджера помощи TiraJira.
"""

import io
from unittest.mock import patch

from tirajira.commands.help_manager import display_help


@patch("sys.stdout", new_callable=io.StringIO)
def test_display_help(mock_stdout):
    """Тест: отображение справочной информации"""
    display_help()

    output = mock_stdout.getvalue()

    # Проверяем, что вывод содержит ключевые элементы справки
    assert "TiraJira (тиражира)" in output
    assert "инструмент для автоматизации массового создания задач в Jira" in output
    assert "Форматы поддерживаемых файлов:" in output
    assert "JSON (.json)" in output
    assert "YAML (.yaml, .yml)" in output
    assert "CSV (.csv)" in output
    assert "Excel (.xlsx)" in output
    assert "Использование:" in output
    assert "python3 main.py <путь_к_файлу>" in output
    assert "Примеры:" in output
    assert "Дополнительная информация:" in output
    assert (
        "Перед использованием необходимо настроить параметры подключения к Jira"
        in output
    )


@patch("sys.stdout", new_callable=io.StringIO)
@patch("tirajira.__version__", "1.0.0")
def test_display_help_version(mock_stdout):
    """Тест: отображение версии в справке"""
    display_help()

    output = mock_stdout.getvalue()

    # Проверяем, что вывод содержит версию
    assert "Версия: 1.0.0" in output
