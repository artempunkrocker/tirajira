"""
Tests for TiraJira help manager.
"""

import io
from unittest.mock import patch

from tirajira import __version__
from tirajira.commands.help_manager import display_help


@patch("sys.stdout", new_callable=io.StringIO)
def test_display_help(mock_stdout):
    """Test: displaying help information"""
    display_help()

    output = mock_stdout.getvalue()

    # Check that output contains key help elements
    assert "TiraJira - tool for automating mass task creation in Jira" in output
    assert "Supported file formats:" in output
    assert "JSON (.json)" in output
    assert "YAML (.yaml, .yml)" in output
    assert "CSV (.csv)" in output
    assert "Excel (.xlsx)" in output
    assert "Usage:" in output
    assert "python3 main.py <path_to_file>" in output
    assert "Examples:" in output
    assert "Additional information:" in output
    assert "Before using, you need to configure Jira connection parameters" in output


@patch("sys.stdout", new_callable=io.StringIO)
def test_display_help_version(mock_stdout):
    """Test: displaying version in help"""
    display_help()

    output = mock_stdout.getvalue()

    # Check that output contains version
    assert f"Version: {__version__}" in output
