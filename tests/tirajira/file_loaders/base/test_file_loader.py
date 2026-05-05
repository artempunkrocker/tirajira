from abc import ABC

import pytest

from tirajira.file_loaders.base import FileLoader


def test_file_loader_is_abstract():
    """Test: check that FileLoader is an abstract class"""
    # Check that the class is abstract
    assert issubclass(FileLoader, ABC)

    # Check that the load_issues method is marked as abstract
    assert hasattr(FileLoader.load_issues, "__isabstractmethod__")
    assert FileLoader.load_issues.__isabstractmethod__ is True

    # Check that we cannot create an instance of the abstract class
    with pytest.raises(
        TypeError,
        match=(
            r"Can't instantiate abstract class FileLoader "
            r"(with abstract method load_issues|without an "
            r"implementation for abstract method 'load_issues')"
        ),
    ):
        FileLoader()
