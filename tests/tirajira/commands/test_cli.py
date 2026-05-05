"""
Tests for TiraJira CLI interface.
"""

from unittest.mock import Mock, patch

import pytest

from tirajira.commands.cli import create_argument_parser, main


def test_create_argument_parser():
    """Test: creating argument parser"""
    parser = create_argument_parser()

    # Check that parser is created
    assert parser is not None

    # Check for presence of main elements
    assert parser.prog == "tirajira"
    assert "Tool for automating mass task creation in Jira" in parser.description


def test_parser_import_command():
    """Test: parsing import command"""
    parser = create_argument_parser()

    # Test with minimal arguments
    args = parser.parse_args(["import", "test.json"])
    assert args.command == "import"
    assert args.file == "test.json"
    assert args.max_concurrent_requests == 10
    assert args.min_request_interval == 1.0
    assert args.stop_on_error is False
    assert args.verbose is False
    assert args.report is None


def test_parser_import_command_with_options():
    """Test: parsing import command with options"""
    parser = create_argument_parser()

    # Test with full set of arguments
    args = parser.parse_args(
        [
            "import",
            "test.json",
            "--max-concurrent-requests",
            "5",
            "--min-request-interval",
            "2.5",
            "--stop-on-error",
            "--verbose",
            "--report",
            "report.json",
        ]
    )

    assert args.command == "import"
    assert args.file == "test.json"
    assert args.max_concurrent_requests == 5
    assert args.min_request_interval == 2.5
    assert args.stop_on_error is True
    assert args.verbose is True
    assert args.report == "report.json"


def test_parser_import_command_with_short_options():
    """Test: parsing import command with short options"""
    parser = create_argument_parser()

    # Test with short arguments
    args = parser.parse_args(["import", "test.json", "-mcr", "3", "-mri", "1.5", "-v"])

    assert args.command == "import"
    assert args.file == "test.json"
    assert args.max_concurrent_requests == 3
    assert args.min_request_interval == 1.5
    assert args.verbose is True


def test_parser_extract_failed_command():
    """Test: parsing extract-failed command"""
    parser = create_argument_parser()

    # Test with extract-failed command arguments
    args = parser.parse_args(["extract-failed", "report.json", "failed.json"])

    assert args.command == "extract-failed"
    assert args.report_file == "report.json"
    assert args.output_file == "failed.json"


def test_parser_resume_command():
    """Test: parsing resume command"""
    parser = create_argument_parser()

    # Test with resume command arguments
    args = parser.parse_args(["resume", "report.json"])

    assert args.command == "resume"
    assert args.report_file == "report.json"


def test_parser_resume_command_with_options():
    """Test: parsing resume command with options"""
    parser = create_argument_parser()

    # Test with resume command arguments and options
    args = parser.parse_args(
        [
            "resume",
            "report.json",
            "--max-concurrent-requests",
            "7",
            "--min-request-interval",
            "0.5",
            "--stop-on-error",
            "--verbose",
            "--report",
            "new_report.json",
        ]
    )

    assert args.command == "resume"
    assert args.report_file == "report.json"
    assert args.max_concurrent_requests == 7
    assert args.min_request_interval == 0.5
    assert args.stop_on_error is True
    assert args.verbose is True
    assert args.report == "new_report.json"


def test_parser_version_argument():
    """Test: parsing --version argument"""
    parser = create_argument_parser()

    # Test with --version argument
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])

    # For --version argument, argparse calls SystemExit with code 0
    assert exc_info.value.code == 0


@patch("tirajira.commands.cli.ImportCommand")
def test_main_import_command(mock_import_command):
    """Test: executing import command through main"""
    mock_import_command_instance = Mock()
    mock_import_command.return_value = mock_import_command_instance

    with patch("sys.argv", ["tirajira", "import", "test.json"]):
        main()

        # Check that ImportCommand was created and called
        mock_import_command.assert_called_once()
        mock_import_command_instance.run.assert_called_once()


@patch("tirajira.commands.cli.ExtractFailedCommand")
def test_main_extract_failed_command(mock_extract_failed_command):
    """Test: executing extract-failed command through main"""
    mock_extract_failed_command_instance = Mock()
    mock_extract_failed_command.return_value = mock_extract_failed_command_instance

    with patch(
        "sys.argv", ["tirajira", "extract-failed", "report.json", "failed.json"]
    ):
        main()

        # Check that ExtractFailedCommand was created and called
        mock_extract_failed_command.assert_called_once()
        mock_extract_failed_command_instance.run.assert_called_once()


@patch("tirajira.commands.cli.ResumeCommand")
def test_main_resume_command(mock_resume_command):
    """Test: executing resume command through main"""
    mock_resume_command_instance = Mock()
    mock_resume_command.return_value = mock_resume_command_instance

    with patch("sys.argv", ["tirajira", "resume", "report.json"]):
        main()

        # Check that ResumeCommand was created and called
        mock_resume_command.assert_called_once()
        mock_resume_command_instance.run.assert_called_once()


def test_main_no_command(capsys):
    """Test: execution without command outputs help"""
    with patch("sys.argv", ["tirajira"]):
        with pytest.raises(SystemExit):
            main()

        # Check that exit code is 1

        # Check for presence of help
        captured = capsys.readouterr()
        assert "usage: tirajira" in captured.out


@patch("argparse.ArgumentParser.print_help")
def test_main_help_command(mock_print_help):
    """Test: execution with help command"""
    with patch("sys.argv", ["tirajira", "--help"]):
        with pytest.raises(SystemExit):
            main()

        # Check that exit code is 0

        # Check that print_help was called
        mock_print_help.assert_called_once()
