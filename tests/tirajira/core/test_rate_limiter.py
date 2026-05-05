"""
Tests for the rate limiter, focusing on the specific
functionality of RateLimiter.
"""

from unittest.mock import Mock, patch

import pytest

from tirajira.core.rate_limiter import RateLimiter
from tirajira.integrations.jira_client_interface import JiraClientInterface


@patch("tirajira.core.rate_limiter.RateLimitController.wait_if_needed")
@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.processing.task_processor.get_logger")
@patch("tirajira.core.rate_limiter.get_logger")
def test_rate_limiter_process_with_timing_control(
    mock_get_logger,
    mock_task_processor_get_logger,
    mock_concurrency_manager_get_logger,
    mock_wait_if_needed,
):
    """Test: processing tasks with timing control"""
    # Mock loggers so they don't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_task_processor_get_logger.return_value = mock_logger
    mock_concurrency_manager_get_logger.return_value = mock_logger

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    mock_jira_client.link_to_epic.return_value = {"success": True}
    mock_jira_client.logger = Mock()

    rate_limiter = RateLimiter(
        jira_client=mock_jira_client,
        max_concurrent_requests=2,
        min_request_interval=1.0,
        verbose=False,
    )

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}, "epic_key": "PROJ-100"},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    rate_limiter.process(issues)

    assert mock_wait_if_needed.call_count == 4
    assert mock_jira_client.create_issue.call_count == 3
    mock_jira_client.link_to_epic.assert_called_once_with("PROJ-123", "PROJ-100")


@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_rate_limiter_process_without_timing_control(
    mock_sleep, mock_time, mock_get_logger
):
    """Test: processing tasks without timing control (min_request_interval=0)"""
    # Mock logger so it doesn't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_time.return_value = 1000.0

    # Mock JiraClient and its create_issue method
    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    mock_jira_client.link_to_epic.return_value = {"success": True}
    mock_jira_client.logger = Mock()

    # Create RateLimiter without timing control
    rate_limiter = RateLimiter(
        jira_client=mock_jira_client,
        max_concurrent_requests=2,
        min_request_interval=0,  # Disable timing control
        verbose=False,
    )

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}, "epic_key": "PROJ-100"},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    rate_limiter.process(issues)

    # Check that delay is not called when min_request_interval=0
    assert mock_sleep.call_count == 0

    # Check the number of create_issue calls
    assert mock_jira_client.create_issue.call_count == 3

    # Check that link_to_epic is called only for tasks with epic_key
    mock_jira_client.link_to_epic.assert_called_once_with("PROJ-123", "PROJ-100")


@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.processing.task_processor.get_logger")
@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
def test_rate_limiter_process_with_processing_parameters(
    mock_time,
    mock_get_logger,
    mock_task_processor_get_logger,
    mock_concurrency_manager_get_logger,
):
    """Test: delegating task processing to ConcurrencyManager"""
    # Mock loggers so they don't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_task_processor_get_logger.return_value = mock_logger
    mock_concurrency_manager_get_logger.return_value = mock_logger

    mock_time.return_value = 1000.0

    # Mock JiraClient and its create_issue method
    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    mock_jira_client.logger = Mock()

    rate_limiter = RateLimiter(
        jira_client=mock_jira_client,
        max_concurrent_requests=2,
        min_request_interval=0,
        verbose=False,
    )

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = rate_limiter.process(issues)

    # Check task processing results
    assert successful_count == 3
    assert len(processing_details) == 3

    # Check that all tasks were processed
    assert mock_jira_client.create_issue.call_count == 3


@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.processing.task_processor.get_logger")
@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_process_parameter_combinations_max_workers_and_queue_size(
    mock_sleep,
    mock_time,
    mock_get_logger,
    mock_task_processor_get_logger,
    mock_concurrency_manager_get_logger,
):
    # Mock logger so it doesn't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_time.side_effect = [1002.0, 1002.0]

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.logger = Mock()

    rate_limiter = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=1.0,
        stop_on_error=False,
        verbose=False,
    )

    rate_limiter._last_request_time = 1000.0

    rate_limiter._wait_if_needed()

    mock_sleep.assert_not_called()
    assert rate_limiter._last_request_time == 1002.0


@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_wait_if_needed_with_zero_or_negative_interval(
    mock_sleep, mock_time, mock_get_logger
):
    """Test: _wait_if_needed doesn't call time.sleep when min_request_interval <= 0"""
    # Mock logger so it doesn't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_time.return_value = 1000.0

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.logger = Mock()

    rate_limiter_zero = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=0,
        stop_on_error=False,
        verbose=False,
    )

    rate_limiter_zero._last_request_time = 500.0
    rate_limiter_zero._wait_if_needed()

    rate_limiter_negative = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=-1.0,
        stop_on_error=False,
        verbose=False,
    )

    rate_limiter_negative._last_request_time = 500.0
    rate_limiter_negative._wait_if_needed()

    mock_sleep.assert_not_called()

    assert rate_limiter_zero._last_request_time == 500.0
    assert rate_limiter_negative._last_request_time == 500.0


@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_wait_if_needed_thread_safety(mock_sleep, mock_time, mock_get_logger):
    """Test: _wait_if_needed uses locking to ensure thread safety"""
    # Mock logger so it doesn't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_time.side_effect = [1000.0, 1000.5, 1001.0, 1001.5]

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.logger = Mock()

    rate_limiter = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=1.0,
        stop_on_error=False,
        verbose=False,
    )

    assert hasattr(rate_limiter, "_lock")

    assert rate_limiter._lock.__class__.__name__ == "lock"

    rate_limiter._last_request_time = 1000.0

    rate_limiter._wait_if_needed()
    rate_limiter._wait_if_needed()

    mock_sleep.assert_called_with(0.5)

    assert rate_limiter._last_request_time == 1001.5


@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.processing.task_processor.get_logger")
@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_process_parameter_combinations_min_request_interval(
    mock_sleep,
    mock_time,
    mock_get_logger,
    mock_task_processor_get_logger,
    mock_concurrency_manager_get_logger,
):
    """Test: process method with different combinations of
    min_request_interval values"""
    # Mock loggers so they don't output to console
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_task_processor_get_logger.return_value = mock_logger
    mock_concurrency_manager_get_logger.return_value = mock_logger

    mock_time.return_value = 1000.0

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }
    mock_jira_client.logger = Mock()

    rate_limiter = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=1.0,
        stop_on_error=False,
        verbose=False,
    )

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    test_values = [0.0, 0.5, 2.0, None]

    for value in test_values:
        rate_limiter.process(issues, min_request_interval=value)
        mock_jira_client.reset_mock()


@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.processing.task_processor.get_logger")
@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_process_with_verbose_parameter_true(
    mock_sleep,
    mock_time,
    mock_get_logger,
    mock_task_processor_get_logger,
    mock_concurrency_manager_get_logger,
):
    """Test: process method with verbose=True in method parameters"""
    mock_time.return_value = 1000.0

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_task_processor_get_logger.return_value = mock_logger
    mock_concurrency_manager_get_logger.return_value = mock_logger

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.logger = Mock()
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }

    rate_limiter = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=0,
        stop_on_error=False,
        verbose=True,
    )

    issues = [{"summary": "Test", "project": {"key": "PROJ"}}]

    rate_limiter.process(issues, verbose=True)

    mock_logger.set_verbose.assert_called_with(True)
    mock_jira_client.logger.set_verbose.assert_called_with(True)


@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.processing.task_processor.get_logger")
@patch("tirajira.core.rate_limiter.get_logger")
@patch("time.time")
@patch("time.sleep")
def test_process_with_verbose_parameter_false(
    mock_sleep,
    mock_time,
    mock_get_logger,
    mock_task_processor_get_logger,
    mock_concurrency_manager_get_logger,
):
    """Test: process method with verbose=False in method parameters"""
    mock_time.return_value = 1000.0

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_task_processor_get_logger.return_value = mock_logger
    mock_concurrency_manager_get_logger.return_value = mock_logger

    mock_jira_client = Mock(spec=JiraClientInterface)
    mock_jira_client.logger = Mock()
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }

    rate_limiter = RateLimiter(
        mock_jira_client,
        max_concurrent_requests=10,
        min_request_interval=0,
        stop_on_error=False,
        verbose=True,
    )

    issues = [{"summary": "Test", "project": {"key": "PROJ"}}]

    rate_limiter.process(issues, verbose=False)

    mock_logger.set_verbose.assert_called_with(False)
    mock_jira_client.logger.set_verbose.assert_called_with(False)


if __name__ == "__main__":
    pytest.main()
