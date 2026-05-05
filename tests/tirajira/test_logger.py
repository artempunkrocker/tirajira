"""
Tests for the logging module.
"""

import logging
from io import StringIO

from tirajira.logger import Logger, get_logger


def test_logger_singleton():
    """Test: Logger implements the Singleton pattern"""
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2


def test_get_logger_function():
    """Test: get_logger function returns a Logger instance"""
    logger = get_logger()
    assert isinstance(logger, Logger)


def test_logger_info_message():
    """Test: output of info message"""
    # Create a string buffer to capture output
    output = StringIO()

    # Create a logger with our buffer
    logger = Logger()
    logger.logger.handlers.clear()  # Clear existing handlers
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Output a message
    logger.info("Test message")

    # Check the result
    assert "Test message" in output.getvalue()


def test_logger_error_message():
    """Test: output of error message"""
    # Create a string buffer to capture output
    output = StringIO()

    # Create a logger with our buffer
    logger = Logger()
    logger.logger.handlers.clear()  # Clear existing handlers
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Output an error message
    logger.error("Test error")

    # Check the result
    assert "❌ Error: Test error" in output.getvalue()


def test_logger_success_message():
    """Test: output of success message"""
    # Create a string buffer to capture output
    output = StringIO()

    # Create a logger with our buffer
    logger = Logger()
    logger.logger.handlers.clear()  # Clear existing handlers
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Output a success message
    logger.success("Test success")

    # Check the result
    assert "✅ Test success" in output.getvalue()


def test_logger_progress_message():
    """Test: output of progress message"""
    # Create a string buffer to capture output
    output = StringIO()

    # Create a logger with our buffer
    logger = Logger()
    logger.logger.handlers.clear()  # Clear existing handlers
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Output a progress message
    logger.progress("Test progress")

    # Check the result
    assert "⏳ Test progress" in output.getvalue()


def test_logger_debug_message_verbose():
    """Test: output of debug message in verbose mode"""
    # Create a string buffer to capture output
    output = StringIO()

    # Create a logger with our buffer
    logger = Logger()
    logger.logger.handlers.clear()  # Clear existing handlers
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Set verbose mode and output a debug message
    logger.set_verbose(True)
    logger.debug("Test debug message")

    # Check the result
    assert "🔍 Debug: Test debug message" in output.getvalue()


def test_logger_debug_message_non_verbose():
    """Test: debug message is not output without verbose mode"""
    # Create a string buffer to capture output
    output = StringIO()

    # Create a logger with our buffer
    logger = Logger()
    logger.logger.handlers.clear()  # Clear existing handlers
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Don't set verbose mode and output a debug message
    logger.set_verbose(False)
    logger.debug("Test debug message")

    # Check that the message is not output
    assert "🔍 Debug: Test debug message" not in output.getvalue()


def test_logger_set_verbose_true():
    """Test: setting verbose mode to True"""
    logger = Logger()
    logger.set_verbose(True)
    assert logger.verbose_mode is True


def test_logger_set_verbose_false():
    """Test: setting verbose mode to False"""
    logger = Logger()
    logger.set_verbose(False)
    assert logger.verbose_mode is False
