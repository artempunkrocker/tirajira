"""
Tests for TiraJira argument parser.
"""

import io
from unittest.mock import patch

from tirajira.commands.argument_parser import ArgumentParser


def test_argument_parser_init():
    """Test: argument parser initialization"""
    parser = ArgumentParser()

    # Check that parser is created
    assert parser is not None
    assert parser.parser is not None


def test_argument_parser_parse_with_file():
    """Test: parsing arguments with file specified"""
    parser = ArgumentParser()

    # Mock command line arguments
    with patch("sys.argv", ["main.py", "test.json"]):
        args = parser.parse()

        assert args.file_path == "test.json"
        assert args.max_concurrent_requests == 10  # default value
        assert args.min_request_interval == 1.0  # default value
        assert args.stop_on_error is False
        assert args.verbose is False
        assert args.report is None
        assert args.help is False
        assert args.version is False


def test_argument_parser_parse_with_options():
    """Test: parsing arguments with options"""
    parser = ArgumentParser()

    # Mock command line arguments with options
    with patch(
        "sys.argv",
        [
            "main.py",
            "test.json",
            "--max-concurrent-requests",
            "5",
            "--min-request-interval",
            "2.5",
            "--stop-on-error",
            "--verbose",
            "--report",
            "report.json",
        ],
    ):
        args = parser.parse()

        assert args.file_path == "test.json"
        assert args.max_concurrent_requests == 5
        assert args.min_request_interval == 2.5
        assert args.stop_on_error is True
        assert args.verbose is True
        assert args.report == "report.json"


def test_argument_parser_parse_with_short_options():
    """Test: parsing arguments with short options"""
    parser = ArgumentParser()

    # Create arguments directly to avoid conflict with pytest
    args = parser.parser.parse_args(
        ["test.json", "-mcr", "3", "-mri", "1.5", "--verbose"]
    )

    assert args.file_path == "test.json"
    assert args.max_concurrent_requests == 3
    assert args.min_request_interval == 1.5
    assert args.verbose is True


def test_argument_parser_parse_report_without_value():
    """Test: parsing --report argument without value"""
    parser = ArgumentParser()

    # Mock command line arguments with --report without value
    with patch("sys.argv", ["main.py", "test.json", "--report"]):
        args = parser.parse()

        assert args.file_path == "test.json"
        assert args.report is True  # When --report is specified without value


def test_argument_parser_parse_help():
    """Test: parsing --help argument"""
    parser = ArgumentParser()

    # Mock command line arguments with --help
    with patch("sys.argv", ["main.py", "--help"]):
        args = parser.parse()

        assert args.help is True


def test_argument_parser_parse_version():
    """Test: parsing --version argument"""
    parser = ArgumentParser()

    # Mock command line arguments with --version
    with patch("sys.argv", ["main.py", "--version"]):
        args = parser.parse()

        assert args.version is True


def test_argument_parser_handle_special_args_help():
    """Test: handling special --help argument"""
    parser = ArgumentParser()

    # Create arguments with --help
    args = parser.parser.parse_args(["--help"])

    # Check that handle_special_args returns True for --help
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        result = parser.handle_special_args(args)

        assert result is True
        output = mock_stdout.getvalue()
        # Check that output contains help
        assert "TiraJira - tool for automating mass task creation in Jira" in output


def test_argument_parser_handle_special_args_version():
    """Test: handling special --version argument"""
    parser = ArgumentParser()

    # Create arguments with --version
    args = parser.parser.parse_args(["--version"])

    # Check that handle_special_args returns True for --version
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        from tirajira import __version__

        result = parser.handle_special_args(args)

        assert result is True
        output = mock_stdout.getvalue()
        # Check that output contains version
        assert f"TiraJira version {__version__}" in output


def test_argument_parser_handle_special_args_no_special():
    """Test: handling regular arguments (not special)"""
    parser = ArgumentParser()

    # Create regular arguments
    args = parser.parser.parse_args(["test.json"])

    # Check that handle_special_args returns False for regular arguments
    result = parser.handle_special_args(args)

    assert result is False


def test_argument_parser_validate_args_valid():
    """Test: validation of valid arguments"""
    parser = ArgumentParser()

    # Create arguments with file specification
    args = parser.parser.parse_args(["test.json"])

    # Check that validation passes successfully
    result = parser.validate_args(args)

    assert result is True


def test_argument_parser_validate_args_invalid_no_file():
    """Test: validation of invalid arguments (no file)"""
    parser = ArgumentParser()

    # Create arguments without file specification
    args = parser.parser.parse_args([])

    # Check that validation fails
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        result = parser.validate_args(args)

        assert result is False
        output = mock_stdout.getvalue()
        # Check that output contains error message
        assert "Error: No path to task file specified" in output
