"""
Tests for base command.
"""

import os
from unittest.mock import Mock, patch

import pytest

from tirajira.commands.base import BaseCommand


def test_base_command_init():
    """Test: base command initialization"""
    args = Mock()
    command = BaseCommand(args)

    assert command.args == args
    assert command.jira_client is None
    assert command.rate_limiter is None
    assert command.task_creator is None


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.auth.jira_authenticator.logger")
@patch("tirajira.integrations.jira_client.JiraAuthenticator")
def test_base_command_initialize_services(mock_auth_factory, mock_logger):
    """Test: initialization of base command services"""
    # Mock logger so it doesn't output to console
    mock_logger.info = Mock()
    mock_logger.error = Mock()

    # Mock authenticator
    mock_jira_client = Mock()
    mock_auth_instance = Mock()
    mock_auth_instance.authenticate.return_value = mock_jira_client
    mock_auth_factory.return_value = mock_auth_instance

    args = Mock()
    args.verbose = False
    args.max_concurrent_requests = 10
    args.min_request_interval = 1
    args.stop_on_error = False

    command = BaseCommand(args)
    command._initialize_services()

    assert command.jira_client is not None
    assert command.rate_limiter is not None
    assert command.task_creator is not None

    # Check that logger was mocked
    mock_logger.info.assert_not_called()


@patch.dict(
    os.environ,
    {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
    },
)
@patch("tirajira.auth.jira_authenticator.logger")
@patch("tirajira.integrations.jira_client.JiraAuthenticator")
def test_base_command_run_template_method(mock_auth_factory, mock_logger):
    """Test: template method run of base command"""
    # Mock logger so it doesn't output to console
    mock_logger.info = Mock()
    mock_logger.error = Mock()

    # Mock authenticator
    mock_jira_client = Mock()
    mock_auth_instance = Mock()
    mock_auth_instance.authenticate.return_value = mock_jira_client
    mock_auth_factory.return_value = mock_auth_instance

    args = Mock()
    args.verbose = False

    class TestCommand(BaseCommand):
        def __init__(self, args):
            super().__init__(args)
            self.execute_called = False

        def execute(self):
            self.execute_called = True
            return "test_result"

    command = TestCommand(args)
    result = command.run()

    assert result == "test_result"
    assert command.execute_called is True
    assert command.jira_client is not None
    assert command.rate_limiter is not None
    assert command.task_creator is not None

    # Check that logger was mocked
    mock_logger.info.assert_not_called()


def test_base_command_execute_not_implemented():
    """Test: execute method must be implemented in subclass"""
    args = Mock()
    command = BaseCommand(args)

    with pytest.raises(NotImplementedError) as exc_info:
        command.execute()

    assert "Method execute must be implemented in subclass" in str(exc_info.value)
