from abc import ABC

import pytest

from tirajira.file_loaders.base import FileLoader


def test_file_loader_is_abstract():
    """Тест: проверка что FileLoader является абстрактным классом"""
    # Проверяем что класс является абстрактным
    assert issubclass(FileLoader, ABC)

    # Проверяем что метод load_issues помечен как абстрактный
    assert hasattr(FileLoader.load_issues, "__isabstractmethod__")
    assert FileLoader.load_issues.__isabstractmethod__ is True

    # Проверяем что нельзя создать экземпляр абстрактного класса
    with pytest.raises(
        TypeError,
        match=(
            r"Can't instantiate abstract class FileLoader "
            r"with abstract method load_issues"
        ),
    ):
        FileLoader()
