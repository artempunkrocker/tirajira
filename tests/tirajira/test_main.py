import os
from unittest.mock import Mock, patch

import pytest

from tirajira.main import create_tasks_from_file, main


@patch("tirajira.main.TaskCreator")
@patch("tirajira.main.RateLimiter")
@patch("tirajira.main.JiraClient")
def test_create_tasks_from_file_success(
    mock_jira_client, mock_rate_limiter, mock_task_creator
):
    """Test: successful creation of tasks from file"""
    # Prepare mock objects
    mock_task_creator_instance = Mock()
    mock_task_creator_instance.create_from_file.return_value = 1
    mock_task_creator.return_value = mock_task_creator_instance

    # Call the function under test
    create_tasks_from_file("test.json")

    # Check that methods were called correctly
    mock_jira_client.assert_called_once()
    mock_rate_limiter.assert_called_once()
    mock_task_creator.assert_called_once()
    mock_task_creator_instance.create_from_file.assert_called_once_with(
        file_path="test.json",
        max_concurrent_requests=10,
        min_request_interval=1.0,
        stop_on_error=False,
        verbose=False,
        report_file=None,
    )


@patch("tirajira.main.TaskCreator")
@patch("tirajira.main.RateLimiter")
@patch("tirajira.main.JiraClient")
def test_create_tasks_from_file_not_found(
    mock_jira_client, mock_rate_limiter, mock_task_creator
):
    """Test: handling file not found error"""
    # Configure mock to throw an exception
    mock_task_creator_instance = Mock()
    mock_task_creator_instance.create_from_file.side_effect = FileNotFoundError(
        "File test.json not found."
    )
    mock_task_creator.return_value = mock_task_creator_instance

    # Check that the function exits with code 1
    with pytest.raises(SystemExit) as excinfo:
        create_tasks_from_file("test.json")
    assert excinfo.value.code == 1


def test_main_no_args(capsys):
    """Test: calling without arguments displays help"""
    with patch("sys.argv", ["main.py"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Check that the exit code is 1
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    # Check for key help elements
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


def test_main_with_file_arg(capsys):
    """Test: calling with file argument through import command"""
    # Check that the program runs without errors with correct arguments
    with patch("sys.argv", ["main.py", "import", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Check that the exit code is 0 (successful completion for --help)
        assert exc_info.value.code == 0

    # Capture output so it doesn't display in the console
    _ = capsys.readouterr()


def test_main_with_help_arg(capsys):
    """Test: calling with --help argument displays help"""
    with patch("sys.argv", ["main.py", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Check that the exit code is 0 (successful completion for --help)
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    # Check for key help elements
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


def test_main_with_version_arg(capsys):
    """Test: calling with --version argument displays version"""
    with patch("sys.argv", ["main.py", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Check that the exit code is 0 (successful completion for --version)
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "tirajira" in captured.out


def test_main_with_short_version_arg(capsys):
    """Test: calling with --version argument displays version"""
    with patch("sys.argv", ["main.py", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Check that the exit code is 0 (successful completion for --version)
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "tirajira" in captured.out


def test_main_module_execution():
    """Test: executing module as script"""
    # Check that the module can be imported without errors
    from tirajira import main

    assert main is not None


def test_main_with_empty_argv(monkeypatch, capsys):
    """Test: calling with empty sys.argv"""
    monkeypatch.setattr("sys.argv", ["main.py"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    # Check that the exit code is 1
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    # Check for key help elements
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


def test_main_with_help_argument(monkeypatch, capsys):
    """Test: calling with --help argument"""
    monkeypatch.setattr("sys.argv", ["main.py", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    # Check that the exit code is 0 (successful completion for --help)
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    # Check for key help elements
    assert "usage: tirajira" in captured.out
    assert "import" in captured.out
    assert "extract-failed" in captured.out
    assert "resume" in captured.out


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_file_argument(mock_import_command, monkeypatch):
    """Test: calling with file argument"""
    monkeypatch.setattr("sys.argv", ["main.py", "import", "test.json"])
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_batch_size_argument(mock_import_command, monkeypatch):
    """Test: calling with batch size argument"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "--max-concurrent-requests", "5"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_delay_argument(mock_import_command, monkeypatch):
    """Test: calling with delay argument"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "--min-request-interval", "2.5"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_both_arguments(mock_import_command, monkeypatch):
    """Test: calling with both arguments"""
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "import",
            "test.json",
            "--max-concurrent-requests",
            "3",
            "--min-request-interval",
            "0.5",
        ],
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_short_arguments(mock_import_command, monkeypatch):
    """Test: calling with short arguments"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "-mcr", "7", "-mri", "1.5"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_stop_on_error_argument(mock_import_command, monkeypatch):
    """Test: calling with --stop-on-error argument"""
    monkeypatch.setattr(
        "sys.argv", ["main.py", "import", "test.json", "--stop-on-error"]
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.commands.cli.ImportCommand")
def test_main_with_all_arguments(mock_import_command, monkeypatch):
    """Test: calling with all arguments"""
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "import",
            "test.json",
            "-mcr",
            "5",
            "-mri",
            "2.0",
            "--stop-on-error",
        ],
    )
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance
    main()
    # Check that ImportCommand was created and called
    mock_import_command.assert_called_once()
    mock_import_command_instance.run.assert_called_once()


def test_main_successful_execution(monkeypatch):
    """Test: checking successful execution of main() without exceptions"""

    # Create a mock function for cli_main that doesn't throw exceptions
    def mock_cli_main():
        pass

    # Patch cli_main
    with patch("tirajira.main.cli_main", side_effect=mock_cli_main):
        # Check that main() executes without exceptions
        try:
            main()
            # If we're here, no exception occurred
            assert True
        except Exception as e:
            # If an exception occurred, the test should fail
            raise AssertionError(f"main() threw exception: {e}") from e
