"""
Тесты для команды импорта TiraJira.
"""

from unittest.mock import Mock, patch

from tirajira.commands.import_cmd import ImportCommand


@patch("tirajira.commands.import_cmd.JiraClient")
@patch("tirajira.commands.import_cmd.BatchProcessor")
@patch("tirajira.commands.import_cmd.TaskCreator")
def test_import_command_execute_success(
    mock_task_creator, mock_batch_processor, mock_jira_client
):
    """Тест: успешное выполнение команды импорта"""
    # Настраиваем mock аргументы
    args = Mock()
    args.file = "test.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Настраиваем mock объекты
    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Создаем команду и выполняем её
    command = ImportCommand(args)
    command.execute()

    # Проверяем, что все компоненты были созданы правильно
    mock_jira_client.assert_called_once_with(verbose=False)
    mock_batch_processor.assert_called_once_with(
        mock_jira_client_instance,
        batch_size=10,
        delay=1.0,
        stop_on_error=False,
        verbose=False,
    )
    mock_task_creator.assert_called_once_with(
        jira_client=mock_jira_client_instance,
        batch_processor=mock_batch_processor_instance,
        verbose=False,
    )

    # Проверяем, что метод create_from_file был вызван с правильными аргументами
    mock_task_creator_instance.create_from_file.assert_called_once_with(
        file_path="test.json",
        batch_size=10,
        delay=1.0,
        stop_on_error=False,
        verbose=False,
        report_file=None,
    )


@patch("tirajira.commands.import_cmd.JiraClient")
@patch("tirajira.commands.import_cmd.BatchProcessor")
@patch("tirajira.commands.import_cmd.TaskCreator")
@patch("tirajira.commands.import_cmd.get_logger")
def test_import_command_execute_with_options(
    mock_get_logger, mock_task_creator, mock_batch_processor, mock_jira_client
):
    """Тест: выполнение команды импорта с опциями"""
    # Настраиваем mock аргументы
    args = Mock()
    args.file = "test.csv"
    args.batch_size = 5
    args.delay = 2.5
    args.stop_on_error = True
    args.verbose = True
    args.report = "report.json"

    # Настраиваем mock объекты
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_batch_processor_instance = Mock()
    mock_batch_processor.return_value = mock_batch_processor_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Создаем команду и выполняем её
    command = ImportCommand(args)
    command.execute()

    # Проверяем, что логгер был вызван правильно
    mock_get_logger.assert_called_once()
    mock_logger.set_verbose.assert_called_once_with(True)

    # Проверяем, что все компоненты были созданы правильно
    mock_jira_client.assert_called_once_with(verbose=True)
    mock_batch_processor.assert_called_once_with(
        mock_jira_client_instance,
        batch_size=5,
        delay=2.5,
        stop_on_error=True,
        verbose=True,
    )
    mock_task_creator.assert_called_once_with(
        jira_client=mock_jira_client_instance,
        batch_processor=mock_batch_processor_instance,
        verbose=True,
    )

    # Проверяем, что метод create_from_file был вызван с правильными аргументами
    mock_task_creator_instance.create_from_file.assert_called_once_with(
        file_path="test.csv",
        batch_size=5,
        delay=2.5,
        stop_on_error=True,
        verbose=True,
        report_file="report.json",
    )


@patch("tirajira.commands.import_cmd.JiraClient")
@patch("tirajira.commands.import_cmd.BatchProcessor")
@patch("tirajira.commands.import_cmd.TaskCreator")
@patch("tirajira.commands.import_cmd.get_logger")
@patch("tirajira.commands.import_cmd.sys.exit")
def test_import_command_execute_exception_handling(
    mock_sys_exit,
    mock_get_logger,
    mock_task_creator,
    mock_batch_processor,
    mock_jira_client,
):
    """Тест: обработка исключений в команде импорта"""
    # Настраиваем mock аргументы
    args = Mock()
    args.file = "nonexistent.json"
    args.batch_size = 10
    args.delay = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Настраиваем mock объекты
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Настраиваем mock, чтобы он выбрасывал исключение
    mock_task_creator_instance = Mock()
    mock_task_creator_instance.create_from_file.side_effect = Exception(
        "File not found"
    )
    mock_task_creator.return_value = mock_task_creator_instance

    # Создаем команду и выполняем её
    command = ImportCommand(args)
    command.execute()

    # Проверяем, что логгер записал ошибку
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once_with(
        "Ошибка при импорте задач: File not found"
    )

    # Проверяем, что sys.exit был вызван с кодом 1
    mock_sys_exit.assert_called_once_with(1)
