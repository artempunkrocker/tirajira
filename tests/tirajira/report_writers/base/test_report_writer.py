"""
Tests for the base ReportWriter class.
"""

from abc import ABC

from tirajira.report_writers.base import ReportWriter


def test_report_writer_is_abstract():
    """Test: ReportWriter class is abstract"""
    # Check that the class is abstract
    assert issubclass(ReportWriter, ABC)


def test_report_writer_has_abstract_method():
    """Test: ReportWriter class has abstract method write_report"""
    # Check that the write_report method is marked as abstract
    assert hasattr(ReportWriter.write_report, "__isabstractmethod__")
    assert ReportWriter.write_report.__isabstractmethod__


def test_report_writer_abstract_method_signature():
    """Test: signature of abstract method write_report"""
    # Check that the method accepts the correct parameters
    import inspect

    sig = inspect.signature(ReportWriter.write_report)
    params = list(sig.parameters.keys())

    # The first parameter should be 'self'
    assert params[0] == "self"

    # The second parameter should be 'report_data'
    assert params[1] == "report_data"

    # The third parameter should be 'file_path'
    assert params[2] == "file_path"
