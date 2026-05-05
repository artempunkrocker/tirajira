"""
Tests for TiraJira import command.
"""

from unittest.mock import Mock, patch

from tirajira.commands.import_cmd import ImportCommand


@patch("tirajira.commands.base.JiraClient")
@patch("tirajira.commands.base.RateLimiter")
@patch("tirajira.commands.base.TaskCreator")
def test_import_command_execute_success(
    mock_task_creator, mock_rate_limiter, mock_jira_client
):
    """Test: successful execution of import command"""
    # Setup mock arguments
    args = Mock()
    args.file = "test.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Setup mock objects
    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_rate_limiter_instance = Mock()
    mock_rate_limiter.return_value = mock_rate_limiter_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Create command and execute it
    command = ImportCommand(args)
    command.run()

    # Check that all components were created correctly
    mock_jira_client.assert_called_once_with(verbose=False)
    mock_rate_limiter.assert_called_once_with(
        mock_jira_client_instance,
        max_concurrent_requests=10,
        min_request_interval=1.0,
        stop_on_error=False,
        verbose=False,
    )
    mock_task_creator.assert_called_once_with(
        jira_client=mock_jira_client_instance,
        rate_limiter=mock_rate_limiter_instance,
        verbose=False,
    )

    # Check that create_from_file method was called with correct arguments
    mock_task_creator_instance.create_from_file.assert_called_once_with(
        file_path="test.json",
        max_concurrent_requests=10,
        min_request_interval=1.0,
        stop_on_error=False,
        verbose=False,
        report_file=None,
    )


@patch("tirajira.commands.base.JiraClient")
@patch("tirajira.commands.base.RateLimiter")
@patch("tirajira.commands.base.TaskCreator")
@patch("tirajira.commands.base.get_logger")
def test_import_command_execute_with_options(
    mock_get_logger, mock_task_creator, mock_rate_limiter, mock_jira_client
):
    """Test: executing import command with options"""
    # Setup mock arguments
    args = Mock()
    args.file = "test.csv"
    args.max_concurrent_requests = 5
    args.min_request_interval = 2.5
    args.stop_on_error = True
    args.verbose = True
    args.report = "report.json"

    # Setup mock objects
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_rate_limiter_instance = Mock()
    mock_rate_limiter.return_value = mock_rate_limiter_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Create command and execute it
    command = ImportCommand(args)
    command.run()

    # Check that logger was called correctly
    mock_get_logger.assert_called_once()
    mock_logger.set_verbose.assert_called_once_with(True)

    # Check that all components were created correctly
    mock_jira_client.assert_called_once_with(verbose=True)
    mock_rate_limiter.assert_called_once_with(
        mock_jira_client_instance,
        max_concurrent_requests=5,
        min_request_interval=2.5,
        stop_on_error=True,
        verbose=True,
    )
    mock_task_creator.assert_called_once_with(
        jira_client=mock_jira_client_instance,
        rate_limiter=mock_rate_limiter_instance,
        verbose=True,
    )

    # Check that create_from_file method was called with correct arguments
    mock_task_creator_instance.create_from_file.assert_called_once_with(
        file_path="test.csv",
        max_concurrent_requests=5,
        min_request_interval=2.5,
        stop_on_error=True,
        verbose=True,
        report_file="report.json",
    )


@patch("tirajira.commands.base.JiraClient")
@patch("tirajira.commands.base.RateLimiter")
@patch("tirajira.commands.base.TaskCreator")
@patch("tirajira.commands.exception_handler.get_logger")
def test_import_command_execute_exception_handling(
    mock_get_logger,
    mock_task_creator,
    mock_rate_limiter,
    mock_jira_client,
):
    """Test: exception handling in import command"""
    # Setup mock arguments
    args = Mock()
    args.file = "nonexistent.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Setup mock objects
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Setup mock to throw an exception
    mock_task_creator_instance = Mock()
    mock_task_creator_instance.create_from_file.side_effect = Exception(
        "File not found"
    )
    mock_task_creator.return_value = mock_task_creator_instance

    # Create command and execute it
    command = ImportCommand(args)
    result = command.run()

    # Check that logger recorded error (now through decorator)
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once_with("Error executing command: File not found")

    assert result == 1
