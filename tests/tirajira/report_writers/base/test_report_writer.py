"""
Тесты для базового класса ReportWriter.
"""

from abc import ABC

from tirajira.report_writers.base import ReportWriter


def test_report_writer_is_abstract():
    """Тест: класс ReportWriter является абстрактным"""
    # Проверяем, что класс является абстрактным
    assert issubclass(ReportWriter, ABC)


def test_report_writer_has_abstract_method():
    """Тест: класс ReportWriter имеет абстрактный метод write_report"""
    # Проверяем, что метод write_report помечен как абстрактный
    assert hasattr(ReportWriter.write_report, "__isabstractmethod__")
    assert ReportWriter.write_report.__isabstractmethod__


def test_report_writer_abstract_method_signature():
    """Тест: сигнатура абстрактного метода write_report"""
    # Проверяем, что метод принимает правильные параметры
    import inspect

    sig = inspect.signature(ReportWriter.write_report)
    params = list(sig.parameters.keys())

    # Первый параметр должен быть 'self'
    assert params[0] == "self"

    # Второй параметр должен быть 'report_data'
    assert params[1] == "report_data"

    # Третий параметр должен быть 'file_path'
    assert params[2] == "file_path"
