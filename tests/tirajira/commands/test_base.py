"""
Тесты для базового класса команды TiraJira.
"""

from unittest.mock import Mock

import pytest

from tirajira.commands.base import BaseCommand


def test_base_command_init():
    """Тест: инициализация базовой команды"""
    args = Mock()
    command = BaseCommand(args)

    assert command.args == args


def test_base_command_execute_not_implemented():
    """Тест: метод execute должен быть реализован в подклассе"""
    args = Mock()
    command = BaseCommand(args)

    with pytest.raises(NotImplementedError) as exc_info:
        command.execute()

    assert "Метод execute должен быть реализован в подклассе" in str(exc_info.value)
