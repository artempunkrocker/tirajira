"""
Tests for TiraJira failed tasks extraction command.
"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from tirajira.commands.extract_failed import ExtractFailedCommand


@patch("tirajira.commands.extract_failed.validate_file_path")
@patch("tirajira.logger.Logger")
def test_extract_failed_command_file_not_found(
    mock_logger_class, mock_validate_file_path
):
    """Test: handling case when report file not found"""
    # Setup mock
    mock_validate_file_path.side_effect = FileNotFoundError("File not found")
    mock_logger = Mock()
    mock_logger_class.return_value = mock_logger

    # Setup arguments
    args = Mock()
    args.report_file = "nonexistent.json"
    args.output_file = "failed.json"

    # Create command and execute it
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Check result
    assert result == 1

    # Check that logger recorded error
    mock_logger_class.assert_called()
    mock_logger.error.assert_called_once()


@patch("tirajira.commands.extract_failed.validate_file_path")
@patch("tirajira.commands.utils.validate_file_path")
@patch(
    "tirajira.commands.utils.open", new_callable=mock_open, read_data='{"tasks": []}'
)
@patch("tirajira.commands.utils.json.load")
@patch("tirajira.logger.Logger")
def test_extract_failed_command_no_failed_tasks(
    mock_logger_class,
    mock_json_load,
    mock_file,
    mock_utils_validate_file_path,
    mock_validate_file_path,
):
    """Test: handling case when no failed tasks in report"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.json")
    mock_json_load.return_value = {"tasks": []}
    mock_logger = Mock()
    mock_logger_class.return_value = mock_logger

    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command and execute it
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Check result
    assert result == 0

    # Check that logger recorded information
    mock_logger_class.assert_called()
    mock_logger.info.assert_called_once_with("No failed tasks found in report")


@patch("tirajira.commands.extract_failed.validate_file_path")
@patch("tirajira.commands.utils.validate_file_path")
@patch(
    "tirajira.commands.utils.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "success"}]}',
)
@patch("tirajira.commands.utils.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.logger.get_logger")
def test_extract_failed_command_with_custom_output_format(
    mock_get_logger,
    mock_create_report_writer,
    mock_json_load,
    mock_file,
    mock_utils_validate_file_path,
    mock_validate_file_path,
):
    """Test: extracting failed tasks with saving in different formats"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.json")
    mock_utils_validate_file_path.return_value = Path("report.json")
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Setup arguments with output file in YAML format
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.yaml"

    # Create command and execute it
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Check result
    assert result == 0

    # Check that report writer was called with correct format
    mock_create_report_writer.assert_called_once_with("yaml")


@patch("tirajira.commands.extract_failed.validate_file_path")
@patch("tirajira.commands.utils.validate_file_path")
@patch(
    "tirajira.commands.utils.open",
    new_callable=mock_open,
    read_data='{"tasks": [{"status": "failure", "issue_data": '
    '{"summary": "Failed task"}}]}',
)
@patch("tirajira.commands.utils.json.load")
@patch("tirajira.commands.extract_failed.create_report_writer")
@patch("tirajira.logger.get_logger")
def test_extract_failed_command_with_unsupported_output_format(
    mock_get_logger,
    mock_create_report_writer,
    mock_json_load,
    mock_file,
    mock_utils_validate_file_path,
    mock_validate_file_path,
):
    """Test: extracting failed tasks with saving in unsupported format"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.json")
    mock_utils_validate_file_path.return_value = Path("report.json")
    mock_json_load.return_value = {
        "tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]
    }

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_writer = Mock()
    mock_create_report_writer.return_value = mock_writer

    # Setup arguments with output file in unsupported format
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.txt"  # Unsupported format

    # Create command and execute it
    command = ExtractFailedCommand(args)
    result = command.execute()

    # Check result
    assert result == 0

    # Check that report writer was called with JSON format (default)
    mock_create_report_writer.assert_called_once_with("json")


@patch("tirajira.commands.utils.validate_file_path")
def test_extract_failed_command_load_json_report_success(mock_validate_file_path):
    """Test: successful JSON report loading"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.json")

    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

    # Test data
    json_data = (
        '{"tasks": [{"status": "failure", "issue_data": {"summary": "Failed task"}}]}'
    )

    # Use patch to simulate file reading
    with patch("tirajira.commands.utils.open", mock_open(read_data=json_data)):
        result = command._load_json_report("report.json")

        # Check result
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["status"] == "failure"


@patch("tirajira.commands.utils.validate_file_path")
def test_extract_failed_command_load_json_report_invalid_format(
    mock_validate_file_path,
):
    """Test: loading JSON report with invalid format"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.json")

    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

    # Test data - array instead of object
    json_data = '[{"status": "failure"}]'

    # Use patch to simulate file reading
    with patch("tirajira.commands.utils.open", mock_open(read_data=json_data)):
        with pytest.raises(Exception) as exc_info:
            command._load_json_report("report.json")

        # Check error message
        assert "JSON report file must contain an object" in str(exc_info.value)


@patch("tirajira.commands.utils.validate_file_path")
def test_extract_failed_command_load_json_report_invalid_json(mock_validate_file_path):
    """Test: loading invalid JSON report"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.json")

    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

    # Test data - invalid JSON
    json_data = '{"tasks": [{status: "failure"}]'  # Invalid JSON

    # Use patch to simulate file reading
    with patch("tirajira.commands.utils.open", mock_open(read_data=json_data)):
        with pytest.raises(ValueError) as exc_info:
            command._load_json_report("report.json")

        # Check error message
        assert "Error parsing JSON report file" in str(exc_info.value)


@patch("tirajira.commands.utils.validate_file_path")
def test_extract_failed_command_load_yaml_report_success(mock_validate_file_path):
    """Test: successful YAML report loading"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.yaml")

    # Setup arguments
    args = Mock()
    args.report_file = "report.yaml"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

    # Test data
    yaml_data = """
tasks:
  - status: failure
    issue_data:
      summary: Failed task
"""

    # Use patch to simulate file reading
    with patch("tirajira.commands.utils.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.utils.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = {
                "tasks": [
                    {"status": "failure", "issue_data": {"summary": "Failed task"}}
                ]
            }
            result = command._load_yaml_report("report.yaml")

            # Check result
            assert "tasks" in result
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["status"] == "failure"


@patch("tirajira.commands.utils.validate_file_path")
def test_extract_failed_command_load_yaml_report_invalid_format(
    mock_validate_file_path,
):
    """Test: loading YAML report with invalid format"""
    # Setup mock
    mock_validate_file_path.return_value = Path("report.yaml")

    # Setup arguments
    args = Mock()
    args.report_file = "report.yaml"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

    # Test data - array instead of object
    yaml_data = """
- status: failure
"""

    # Use patch to simulate file reading
    with patch("tirajira.commands.utils.open", mock_open(read_data=yaml_data)):
        with patch("tirajira.commands.utils.yaml.safe_load") as mock_safe_load:
            mock_safe_load.return_value = [{"status": "failure"}]
            with pytest.raises(Exception) as exc_info:
                command._load_yaml_report("report.yaml")

            # Check error message
            assert "YAML report file must contain an object" in str(exc_info.value)


def test_extract_failed_command_extract_failed_tasks_empty_list():
    """Test: extracting failed tasks from empty list"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

    # Empty task list
    tasks = []

    # Call extraction method
    result = command._extract_failed_tasks(tasks)

    # Check result
    assert len(result) == 0


def test_extract_failed_command_extract_failed_tasks_mixed_status():
    """Test: extracting failed tasks from mixed status list"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

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


def test_extract_failed_command_extract_failed_tasks_no_issue_data():
    """Test: extracting failed tasks without issue_data field"""
    # Setup arguments
    args = Mock()
    args.report_file = "report.json"
    args.output_file = "failed.json"

    # Create command
    command = ExtractFailedCommand(args)

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
