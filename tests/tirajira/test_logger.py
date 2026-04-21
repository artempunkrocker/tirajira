"""
Тесты для модуля логирования.
"""

import logging
from io import StringIO

from tirajira.logger import Logger, get_logger


def test_logger_singleton():
    """Тест: Logger реализует паттерн Singleton"""
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2


def test_get_logger_function():
    """Тест: функция get_logger возвращает экземпляр Logger"""
    logger = get_logger()
    assert isinstance(logger, Logger)


def test_logger_info_message():
    """Тест: вывод информационного сообщения"""
    # Создаем строковый буфер для захвата вывода
    output = StringIO()

    # Создаем логгер с нашим буфером
    logger = Logger()
    logger.logger.handlers.clear()  # Очищаем существующие обработчики
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Выводим сообщение
    logger.info("Тестовое сообщение")

    # Проверяем результат
    assert "Тестовое сообщение" in output.getvalue()


def test_logger_error_message():
    """Тест: вывод сообщения об ошибке"""
    # Создаем строковый буфер для захвата вывода
    output = StringIO()

    # Создаем логгер с нашим буфером
    logger = Logger()
    logger.logger.handlers.clear()  # Очищаем существующие обработчики
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Выводим сообщение об ошибке
    logger.error("Тестовая ошибка")

    # Проверяем результат
    assert "❌ Ошибка: Тестовая ошибка" in output.getvalue()


def test_logger_success_message():
    """Тест: вывод сообщения об успехе"""
    # Создаем строковый буфер для захвата вывода
    output = StringIO()

    # Создаем логгер с нашим буфером
    logger = Logger()
    logger.logger.handlers.clear()  # Очищаем существующие обработчики
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Выводим сообщение об успехе
    logger.success("Тестовый успех")

    # Проверяем результат
    assert "✅ Тестовый успех" in output.getvalue()


def test_logger_progress_message():
    """Тест: вывод сообщения о прогрессе"""
    # Создаем строковый буфер для захвата вывода
    output = StringIO()

    # Создаем логгер с нашим буфером
    logger = Logger()
    logger.logger.handlers.clear()  # Очищаем существующие обработчики
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Выводим сообщение о прогрессе
    logger.progress("Тестовый прогресс")

    # Проверяем результат
    assert "⏳ Тестовый прогресс" in output.getvalue()


def test_logger_debug_message_verbose():
    """Тест: вывод отладочного сообщения в verbose режиме"""
    # Создаем строковый буфер для захвата вывода
    output = StringIO()

    # Создаем логгер с нашим буфером
    logger = Logger()
    logger.logger.handlers.clear()  # Очищаем существующие обработчики
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Устанавливаем verbose режим и выводим отладочное сообщение
    logger.set_verbose(True)
    logger.debug("Тестовое отладочное сообщение")

    # Проверяем результат
    assert "🔍 Debug: Тестовое отладочное сообщение" in output.getvalue()


def test_logger_debug_message_non_verbose():
    """Тест: отладочное сообщение не выводится без verbose режима"""
    # Создаем строковый буфер для захвата вывода
    output = StringIO()

    # Создаем логгер с нашим буфером
    logger = Logger()
    logger.logger.handlers.clear()  # Очищаем существующие обработчики
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.logger.addHandler(handler)

    # Не устанавливаем verbose режим и выводим отладочное сообщение
    logger.set_verbose(False)
    logger.debug("Тестовое отладочное сообщение")

    # Проверяем, что сообщение не выведено
    assert "🔍 Debug: Тестовое отладочное сообщение" not in output.getvalue()


def test_logger_set_verbose_true():
    """Тест: установка verbose режима в True"""
    logger = Logger()
    logger.set_verbose(True)
    assert logger.verbose_mode is True


def test_logger_set_verbose_false():
    """Тест: установка verbose режима в False"""
    logger = Logger()
    logger.set_verbose(False)
    assert logger.verbose_mode is False
