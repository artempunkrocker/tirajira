"""
Tests for TiraJira resume execution command.
"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from tirajira.commands.resume import ResumeCommand


@patch("tirajira.commands.resume.validate_file_path")
@patch("tirajira.commands.base.get_logger")
def test_resume_command_file_not_found(mock_get_logger, mock_validate_file_path):
    """Test: handling case when report file not found"""
    # Setup mock
    mock_validate_file_path.side_effect = FileNotFoundError("File not found")
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Setup arguments
    args = Mock()
    args.report_file = "invalid.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command and execute it
    command = ResumeCommand(args)
    result = command.execute()

    # Check result
    assert result == 1

    # Check that logger recorded error
    mock_get_logger.assert_called_once()
    mock_logger.error.assert_called_once()


@patch("tirajira.commands.resume.validate_file_path")
@patch(
    "tirajira.commands.resume.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.resume.json.load")
@patch("tirajira.commands.base.JiraClient")
@patch("tirajira.commands.base.RateLimiter")
@patch("tirajira.commands.base.TaskCreator")
@patch("tirajira.commands.base.get_logger")
def test_resume_command_with_yaml_report(
    mock_get_logger,
    mock_task_creator,
    mock_rate_limiter,
    mock_jira_client,
    mock_json_load,
    mock_file,
    mock_validate_file_path,
):
    """Test: processing failed tasks from YAML report"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.yaml")
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}],
        "metadata": {"source_file": "original.yaml"},
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_jira_client_instance = Mock()
    mock_jira_client.return_value = mock_jira_client_instance

    mock_rate_limiter_instance = Mock()
    mock_rate_limiter_instance.process.return_value = (1, [{"status": "success"}])
    mock_rate_limiter.return_value = mock_rate_limiter_instance

    mock_task_creator_instance = Mock()
    mock_task_creator.return_value = mock_task_creator_instance

    # Setup arguments
    args = Mock()
    args.report_file = "report.yaml"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command and execute it
    command = ResumeCommand(args)
    result = command.run()

    # Check result
    assert result == 0

    # Check that logger recorded information
    mock_get_logger.assert_called_once()
    mock_logger.info.assert_called_once_with("Found 1 failed tasks for reprocessing")
    mock_logger.success.assert_called_once_with("Successfully processed 1 of 1 tasks")

    # Setup arguments with report
    args = Mock()
    args.report_file = "report.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = "new_report.json"

    # Create command and execute it
    command = ResumeCommand(args)
    result = command.run()

    # Check result
    assert result == 0

    # Check that _save_report method was called with correct source_file
    mock_task_creator_instance._save_report.assert_called_once_with(
        "original.yaml",  # source_file from metadata
        [{"status": "success"}],  # processing_details
        "new_report.json",  # report_file
        1,  # successful_count
        1,  # total_count
    )


def test_resume_command_load_json_report_success():
    """Test: successful loading of JSON report"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Test data - array instead of object
    json_data = '[{"status": "failure"}]'

    # Use patch to mock file reading
    with patch("tirajira.commands.resume.open", mock_open(read_data=json_data)):
        with pytest.raises(Exception) as exc_info:
            command._load_json_report("report.json")

        # Check error message
        assert "JSON report file must contain an object" in str(exc_info.value)


def test_resume_command_load_json_report_invalid_json():
    """Test: loading invalid JSON report"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Test data - invalid JSON
    json_data = '{"tasks": [{status: "failure"}]'  # Invalid JSON

    # Use patch to mock file reading
    with patch("tirajira.commands.resume.open", mock_open(read_data=json_data)):
        with pytest.raises(ValueError) as exc_info:
            command._load_json_report("report.json")

        # Check error message
        assert "Error parsing JSON report file" in str(exc_info.value)


def test_resume_command_load_yaml_report_success():
    """Test: successful loading of YAML report"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.yaml"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Test data
    yaml_data = """
tasks:
  - status: failure
    issue_data:
      summary: Failed task
"""

    # Use patch to mock file reading
    with patch("tirajira.commands.resume.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.resume.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = {
                "tasks": [
                    {"status": "failure", "issue_data": {"summary": "Failed task"}}
                ],
                "metadata": {"source_file": "original.yaml"},
            }
            result = command._load_yaml_report("report.yaml")

            # Check result
            assert "tasks" in result
            assert "metadata" in result
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["status"] == "failure"
            assert result["metadata"]["source_file"] == "original.yaml"


def test_resume_command_load_yaml_report_invalid_format():
    """Test: loading YAML report with invalid format"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.yaml"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Test data - array instead of object
    yaml_data = """
- status: failure
"""

    # Use patch to mock file reading
    with patch("tirajira.commands.resume.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.resume.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = [{"status": "failure"}]
            with pytest.raises(Exception) as exc_info:
                command._load_yaml_report("report.yaml")

            # Check error message
            assert "YAML report file must contain an object" in str(exc_info.value)


def test_resume_command_extract_failed_tasks_empty_list():
    """Test: extracting failed tasks from empty list"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Empty task list
    tasks = []

    # Call extraction method
    result = command._extract_failed_tasks(tasks)

    # Check result
    assert len(result) == 0


def test_resume_command_extract_failed_tasks_mixed_status():
    """Test: extracting failed tasks from mixed status list"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Mixed task list
    tasks = [
        {"status": "success", "issue_data": {"summary": "Success task"}},
        {"status": "failure", "issue_data": {"summary": "Failed task 1"}},
        {"status": "pending", "issue_data": {"summary": "Pending task"}},
        {"status": "failure", "issue_data": {"summary": "Failed task 2"}},
        {"status": "completed", "issue_data": {"summary": "Completed task"}},
    ]

    # Call extraction method
    result = command._extract_failed_tasks(tasks)

    # Check result
    assert len(result) == 2
    assert result[0]["summary"] == "Failed task 1"
    assert result[1]["summary"] == "Failed task 2"


def test_resume_command_extract_failed_tasks_no_issue_data():
    """Test: extracting failed tasks without issue_data field"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.max_concurrent_requests = 10
    args.min_request_interval = 1.0
    args.stop_on_error = False
    args.verbose = False
    args.report = None

    # Create command
    command = ResumeCommand(args)

    # Tasks without issue_data field
    tasks = [
        {"status": "failure", "summary": "Failed task", "project": {"key": "PROJ"}},
        {"status": "success", "summary": "Success task", "project": {"key": "PROJ"}},
    ]

    # Call extraction method
    result = command._extract_failed_tasks(tasks)

    # Check result
    assert len(result) == 1
    assert result[0]["summary"] == "Failed task"
    assert result[0]["project"]["key"] == "PROJ"
    assert "status" not in result[0]  # Status field should be removed
