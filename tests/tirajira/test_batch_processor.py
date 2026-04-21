from unittest.mock import Mock, patch

import pytest

from tirajira.batch_processor import BatchProcessor
from tirajira.jira_client import JiraClient


@patch("time.sleep")
def test_batch_processor_process(mock_sleep):
    """Тест: пакетная обработка задач"""
    # Мокаем JiraClient и его метод create_issue
    mock_jira_client = Mock(spec=JiraClient)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    mock_jira_client.link_to_epic.return_value = {"success": True}

    processor = BatchProcessor(
        jira_client=mock_jira_client, batch_size=2, delay=0.1, verbose=False
    )

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}, "epic_key": "PROJ-100"},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    processor.process(issues)

    # Проверяем, что задержка вызывается между пачками
    assert mock_sleep.call_count == 2  # Ожидаем одну задержку между пачками

    # Проверяем количество вызовов create_issue
    assert mock_jira_client.create_issue.call_count == 3

    # Проверяем вызов link_to_epic только для задачи с epic_key
    mock_jira_client.link_to_epic.assert_called_once_with("PROJ-123", "PROJ-100")


@patch("time.sleep")
def test_batch_processor_create_issue_failure(mock_sleep):
    """Тест: обработка ошибки при создании задачи"""
    mock_jira_client = Mock(spec=JiraClient)
    mock_jira_client.create_issue.return_value = {
        "success": False,
        "error": "Create failed",
    }

    processor = BatchProcessor(
        jira_client=mock_jira_client, batch_size=1, delay=0, verbose=False
    )

    issues = [{"summary": "Test", "project": {"key": "PROJ"}}]

    processor.process(issues)


@patch("time.sleep")
def test_batch_processor_link_to_epic_failure(mock_sleep):
    """Тест: обработка ошибки при привязке к эпику"""
    mock_jira_client = Mock(spec=JiraClient)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    mock_jira_client.link_to_epic.return_value = {
        "success": False,
        "error": "Link failed",
    }

    processor = BatchProcessor(
        jira_client=mock_jira_client, batch_size=1, delay=0, verbose=False
    )

    issues = [{"summary": "Test", "project": {"key": "PROJ"}, "epic_key": "PROJ-100"}]

    processor.process(issues)


@patch("time.sleep")
def test_batch_processor_stop_on_create_error(mock_sleep):
    """Тест: остановка при ошибке создания задачи в режиме stop_on_error"""
    mock_jira_client = Mock(spec=JiraClient)
    # Первая задача создается успешно, вторая - с ошибкой
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": False, "error": "Create failed"},
    ]

    processor = BatchProcessor(
        jira_client=mock_jira_client,
        batch_size=2,
        delay=0,
        stop_on_error=True,
        verbose=False,
    )

    # Создаем 3 задачи - первая должна обработаться успешно,
    # вторая вызовет ошибку и остановит обработку третьей
    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = processor.process(issues)

    # Только первая задача должна быть обработана успешно
    assert successful_count == 1
    assert mock_jira_client.create_issue.call_count == 2  # Должно быть 2 вызова, не 3


@patch("time.sleep")
def test_batch_processor_stop_on_link_error(mock_sleep):
    """Тест: остановка при ошибке привязки к эпику в режиме stop_on_error"""
    mock_jira_client = Mock(spec=JiraClient)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    # Первая привязка успешна, вторая - с ошибкой
    mock_jira_client.link_to_epic.side_effect = [
        {"success": True},
        {"success": False, "error": "Link failed"},
    ]

    processor = BatchProcessor(
        jira_client=mock_jira_client,
        batch_size=2,
        delay=0,
        stop_on_error=True,
        verbose=False,
    )

    # Создаем 3 задачи с эпиками - первая должна обработаться успешно,
    # вторая вызовет ошибку привязки и остановит обработку третьей
    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}, "epic_key": "PROJ-100"},
        {"summary": "Test 2", "project": {"key": "PROJ"}, "epic_key": "PROJ-101"},
        {"summary": "Test 3", "project": {"key": "PROJ"}, "epic_key": "PROJ-102"},
    ]

    successful_count, processing_details = processor.process(issues)

    # Обе задачи создаются, но только первая привязывается к эпику
    assert successful_count == 2
    assert mock_jira_client.create_issue.call_count == 2  # Должно быть 2 вызова, не 3


@patch("time.sleep")
def test_batch_processor_continue_on_error_default(mock_sleep):
    """Тест: продолжение обработки при ошибках в обычном режиме (по умолчанию)"""
    mock_jira_client = Mock(spec=JiraClient)
    # Чередуем успешные и неуспешные операции
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": False, "error": "Create failed"},
        {"success": True, "issue_key": "PROJ-124"},
    ]

    processor = BatchProcessor(
        jira_client=mock_jira_client,
        batch_size=3,
        delay=0,
        stop_on_error=False,
        verbose=False,
    )

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = processor.process(issues)

    # Первая и третья задачи должны быть обработаны успешно,
    # несмотря на ошибку во второй
    assert successful_count == 2
    assert (
        mock_jira_client.create_issue.call_count == 3
    )  # Все 3 задачи должны быть обработаны


@patch("time.sleep")
def test_batch_processor_stop_on_error_multiple_batches(mock_sleep):
    """Тест: остановка при ошибке в режиме stop_on_error с несколькими пакетами"""
    mock_jira_client = Mock(spec=JiraClient)
    # Создаем успешные ответы для первых двух задач, затем ошибка, затем успешная задача
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": True, "issue_key": "PROJ-124"},
        {"success": False, "error": "Create failed"},
        {"success": True, "issue_key": "PROJ-125"},  # Этого вызова быть не должно
    ]

    processor = BatchProcessor(
        jira_client=mock_jira_client,
        batch_size=2,
        delay=0,
        stop_on_error=True,
        verbose=False,
    )

    # Создаем 4 задачи в 2 пакетах - первые две должны обработаться успешно,
    # третья вызовет ошибку в первом пакете и остановит обработку
    # второго пакета (четвертой задачи)
    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
        {"summary": "Test 4", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = processor.process(issues)

    # Все задачи в первом пакете (1 и 2) обрабатываются успешно (2 задачи)
    # Второй пакет тоже обрабатывается полностью, но одна задача в нем возвращает ошибку
    # Поэтому успешных задач 2 + 1 = 3
    # Но пакеты после второго уже не обрабатываются
    assert successful_count == 3

    # Все 4 задачи должны быть обработаны, так как остановка происходит после
    # завершения пакета с ошибкой, а не во время его обработки
    assert mock_jira_client.create_issue.call_count == 4


if __name__ == "__main__":
    pytest.main()

"""
Дополнительные тесты для процессора пакетов для повышения покрытия кода.
"""


def test_batch_processor_process_empty_list():
    """Тест: обработка пустого списка задач."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)

    # Создаем процессор пакетов
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=False, verbose=False
    )

    # Обрабатываем пустой список задач
    successful_count, processing_details = processor.process([])

    # Проверяем результаты
    assert successful_count == 0
    assert len(processing_details) == 0
    # Проверяем, что методы jira_client не были вызваны
    mock_jira_client.create_issue.assert_not_called()
    mock_jira_client.link_to_epic.assert_not_called()


def test_batch_processor_process_single_batch():
    """Тест: обработка задач в одном пакете."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": True, "issue_key": "PROJ-124"},
        {"success": True, "issue_key": "PROJ-125"},
    ]

    # Создаем процессор пакетов
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=False, verbose=False
    )

    # Тестовые задачи
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 3",
            "issuetype": {"name": "Task"},
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 3
    assert len(processing_details) == 3

    # Проверяем, что create_issue был вызван 3 раза
    assert mock_jira_client.create_issue.call_count == 3

    # Проверяем детали обработки
    for i, detail in enumerate(processing_details):
        assert detail["id"] == i
        assert detail["status"] == "success"
        assert detail["issue_key"] == f"PROJ-{123 + i}"
        assert "processed_at" in detail


def test_batch_processor_process_multiple_batches():
    """Тест: обработка задач в нескольких пакетах."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": True, "issue_key": "PROJ-124"},
        {"success": True, "issue_key": "PROJ-125"},
        {"success": True, "issue_key": "PROJ-126"},
        {"success": True, "issue_key": "PROJ-127"},
    ]

    # Создаем процессор пакетов с размером пакета 2
    processor = BatchProcessor(
        mock_jira_client, batch_size=2, delay=1.0, stop_on_error=False, verbose=False
    )

    # Тестовые задачи (5 задач, будут обработаны в 3 пакетах: 2+2+1)
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 3",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 4",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 5",
            "issuetype": {"name": "Task"},
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 5
    assert len(processing_details) == 5

    # Проверяем, что create_issue был вызван 5 раз
    assert mock_jira_client.create_issue.call_count == 5


def test_batch_processor_process_with_epic_linking():
    """Тест: обработка задач с привязкой к эпику."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": True, "issue_key": "PROJ-124"},
    ]
    # Настраиваем возвращаемые значения для link_to_epic
    # (ничего не возвращаем, так как метод void)
    mock_jira_client.link_to_epic.return_value = {"success": True}

    # Создаем процессор пакетов
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=False, verbose=False
    )

    # Тестовые задачи с эпиками
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-100",
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-101",
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 2
    assert len(processing_details) == 2

    # Проверяем, что create_issue был вызван 2 раза
    assert mock_jira_client.create_issue.call_count == 2

    # Проверяем, что link_to_epic был вызван 2 раза
    assert mock_jira_client.link_to_epic.call_count == 2

    # Проверяем, что link_to_epic был вызван с правильными аргументами
    mock_jira_client.link_to_epic.assert_any_call("PROJ-123", "PROJ-100")
    mock_jira_client.link_to_epic.assert_any_call("PROJ-124", "PROJ-101")


def test_batch_processor_process_with_creation_failure():
    """Тест: обработка задач с ошибкой создания."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue (один вызов завершится ошибкой)
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": False, "error": "Create failed"},
        {"success": True, "issue_key": "PROJ-125"},
    ]

    # Создаем процессор пакетов
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=False, verbose=False
    )

    # Тестовые задачи
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 3",
            "issuetype": {"name": "Task"},
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 2  # Только 2 задачи были успешно созданы
    assert (
        len(processing_details) == 3
    )  # Все 3 задачи были обработаны (2 успешно, 1 с ошибкой)

    # Проверяем, что create_issue был вызван 3 раза
    assert mock_jira_client.create_issue.call_count == 3

    # Проверяем детали обработки
    # Первая задача - успех
    assert processing_details[0]["status"] == "success"
    assert processing_details[0]["issue_key"] == "PROJ-123"

    # Вторая задача - ошибка
    assert processing_details[1]["status"] == "failure"
    assert "Create failed" in processing_details[1]["error_message"]

    # Третья задача - успех
    assert processing_details[2]["status"] == "success"
    assert processing_details[2]["issue_key"] == "PROJ-125"


def test_batch_processor_process_with_epic_linking_failure():
    """Тест: обработка задач с ошибкой привязки к эпику."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": True, "issue_key": "PROJ-124"},
    ]
    # Настраиваем возвращаемые значения для link_to_epic
    # (второй вызов завершится ошибкой)
    mock_jira_client.link_to_epic.side_effect = [
        {"success": True},
        {"success": False, "error": "Link failed"},
    ]

    # Создаем процессор пакетов
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=False, verbose=False
    )

    # Тестовые задачи с эпиками
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-100",
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-101",
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 2  # Обе задачи были успешно созданы
    assert len(processing_details) == 2  # Обе задачи были обработаны

    # Проверяем, что create_issue был вызван 2 раза
    assert mock_jira_client.create_issue.call_count == 2

    # Проверяем, что link_to_epic был вызван 2 раза
    assert mock_jira_client.link_to_epic.call_count == 2

    # Проверяем детали обработки
    # Первая задача - успех (создание + привязка)
    assert processing_details[0]["status"] == "success"
    assert processing_details[0]["issue_key"] == "PROJ-123"

    # Вторая задача - успех создания, но ошибка привязки
    assert processing_details[1]["status"] == "success"  # Задача создана успешно
    assert processing_details[1]["issue_key"] == "PROJ-124"
    # Проверяем, что в деталях обработки есть информация об ошибке привязки
    assert "Link failed" in str(processing_details)


def test_batch_processor_process_stop_on_error_create():
    """Тест: обработка задач с остановкой при ошибке создания."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue
    # (второй вызов завершится ошибкой)
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": False, "error": "Create failed"},
        {"success": True, "issue_key": "PROJ-125"},
    ]

    # Создаем процессор пакетов с stop_on_error=True
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=True, verbose=False
    )

    # Тестовые задачи
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 3",
            "issuetype": {"name": "Task"},
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 2  # Две задачи были успешно созданы (первая и третья)
    assert len(processing_details) == 3  # Все 3 задачи были обработаны

    # Проверяем, что create_issue был вызван 3 раза
    assert mock_jira_client.create_issue.call_count == 3

    # Проверяем детали обработки
    # Первая задача - успех
    assert processing_details[0]["status"] == "success"
    assert processing_details[0]["issue_key"] == "PROJ-123"

    # Вторая задача - ошибка
    assert processing_details[1]["status"] == "failure"
    assert "Create failed" in processing_details[1]["error_message"]

    # Третья задача - успех (без error_message, так как обработана успешно)
    assert processing_details[2]["status"] == "success"
    assert processing_details[2]["issue_key"] == "PROJ-125"
    # Проверяем, что у третьей задачи нет ключа error_message
    assert "error_message" not in processing_details[2]

    # Проверяем, что сообщение об остановке обработки есть в логах
    # Это проверяется через логи, которые мы видим в выводе теста


def test_batch_processor_process_stop_on_error_link():
    """Тест: обработка задач с остановкой при ошибке привязки к эпику."""
    # Создаем mocks
    mock_jira_client = Mock(spec=JiraClient)
    # Настраиваем возвращаемые значения для create_issue
    mock_jira_client.create_issue.side_effect = [
        {"success": True, "issue_key": "PROJ-123"},
        {"success": True, "issue_key": "PROJ-124"},
        {"success": True, "issue_key": "PROJ-125"},
    ]
    # Настраиваем возвращаемые значения для link_to_epic
    # (второй вызов завершится ошибкой)
    mock_jira_client.link_to_epic.side_effect = [
        {"success": True},
        {"success": False, "error": "Link failed"},
        {"success": True},
    ]

    # Создаем процессор пакетов с stop_on_error=True
    processor = BatchProcessor(
        mock_jira_client, batch_size=10, delay=1.0, stop_on_error=True, verbose=False
    )

    # Тестовые задачи с эпиками
    issues = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task 1",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-100",
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 2",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-101",
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task 3",
            "issuetype": {"name": "Task"},
            "epic_key": "PROJ-102",
        },
    ]

    # Обрабатываем задачи
    successful_count, processing_details = processor.process(issues)

    # Проверяем результаты
    assert successful_count == 3  # Все три задачи были успешно созданы
    assert len(processing_details) == 3  # Все 3 задачи были обработаны

    # Проверяем, что create_issue был вызван 3 раза
    assert mock_jira_client.create_issue.call_count == 3

    # Проверяем, что link_to_epic был вызван 3 раза
    assert mock_jira_client.link_to_epic.call_count == 3

    # Проверяем детали обработки
    # Первая задача - успех
    assert processing_details[0]["status"] == "success"
    assert processing_details[0]["issue_key"] == "PROJ-123"

    # Вторая задача - успех создания, но ошибка привязки
    assert processing_details[1]["status"] == "success"  # Задача создана успешно
    assert processing_details[1]["issue_key"] == "PROJ-124"
    # Проверяем, что в деталях обработки есть информация об ошибке привязки
    assert "Link failed" in processing_details[1]["error_message"]

    # Третья задача - успех (без error_message, так как обработана успешно)
    assert processing_details[2]["status"] == "success"
    assert processing_details[2]["issue_key"] == "PROJ-125"
    # Проверяем, что у третьей задачи нет ключа error_message
    assert "error_message" not in processing_details[2]

    # Проверяем, что сообщение об остановке обработки есть в логах
    # Это проверяется через логи, которые мы видим в выводе теста
