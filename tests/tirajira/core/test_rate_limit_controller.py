"""
Tests for the rate limit controller.
"""

from unittest.mock import patch

import pytest

from tirajira.core.rate_limit_controller import RateLimitController


@patch("time.time")
@patch("time.sleep")
def test_rate_limit_controller_wait_if_needed_no_sleep(mock_sleep, mock_time):
    """Test: wait_if_needed does not call time.sleep when min_request_interval <= 0"""
    mock_time.return_value = 1000.0

    # Test with min_request_interval = 0
    rate_controller_zero = RateLimitController(min_request_interval=0)
    rate_controller_zero._last_request_time = 500.0
    rate_controller_zero.wait_if_needed()
    mock_sleep.assert_not_called()

    # Test with min_request_interval < 0
    rate_controller_negative = RateLimitController(min_request_interval=-1.0)
    rate_controller_negative._last_request_time = 500.0
    rate_controller_negative.wait_if_needed()
    mock_sleep.assert_not_called()


@patch("time.time")
@patch("time.sleep")
def test_rate_limit_controller_wait_if_needed_with_positive_interval(
    mock_sleep, mock_time
):
    """Test: wait_if_needed calls time.sleep when min_request_interval > 0"""
    mock_time.side_effect = [1000.5, 1001.0]

    rate_controller = RateLimitController(min_request_interval=1.0)
    rate_controller._last_request_time = 1000.0

    rate_controller.wait_if_needed()

    mock_sleep.assert_called_once_with(0.5)
    assert rate_controller._last_request_time == 1001.0


@patch("time.time")
@patch("time.sleep")
def test_rate_limit_controller_wait_if_needed_no_sleep_when_time_already_passed(
    mock_sleep, mock_time
):
    """Test: wait_if_needed does not call time.sleep when time has already passed"""
    mock_time.side_effect = [1002.0, 1002.0]

    rate_controller = RateLimitController(min_request_interval=1.0)
    rate_controller._last_request_time = 1000.0

    rate_controller.wait_if_needed()

    mock_sleep.assert_not_called()
    assert rate_controller._last_request_time == 1002.0


@patch("time.time")
@patch("time.sleep")
def test_rate_limit_controller_thread_safety(mock_sleep, mock_time):
    """Test: wait_if_needed uses locking to ensure thread safety"""
    mock_time.side_effect = [1000.0, 1000.5, 1001.0, 1001.5]

    rate_controller = RateLimitController(min_request_interval=1.0)

    assert hasattr(rate_controller, "_lock")
    assert rate_controller._lock.__class__.__name__ == "lock"

    rate_controller._last_request_time = 1000.0

    rate_controller.wait_if_needed()
    rate_controller.wait_if_needed()

    mock_sleep.assert_called_with(0.5)
    assert rate_controller._last_request_time == 1001.5


@patch("time.time")
@patch("time.sleep")
def test_rate_limit_controller_update_min_request_interval(mock_sleep, mock_time):
    """Test: update_min_request_interval correctly updates the interval"""
    mock_time.return_value = 1000.0

    rate_controller = RateLimitController(min_request_interval=1.0)
    assert rate_controller.min_request_interval == 1.0

    rate_controller.update_min_request_interval(2.5)
    assert rate_controller.min_request_interval == 2.5

    rate_controller.update_min_request_interval(0.0)
    assert rate_controller.min_request_interval == 0.0


@patch("time.time")
@patch("time.sleep")
def test_rate_limit_controller_multiple_calls(mock_sleep, mock_time):
    """Test: multiple consecutive calls to wait_if_needed"""
    # Simulate a sequence of time:
    # initial time, time after time.time() inside wait_if_needed,
    # time after time.sleep() inside wait_if_needed,
    # time after updating _last_request_time
    mock_time.side_effect = [1000.0, 1000.0, 1001.0, 1001.0, 1001.0, 1002.0]

    rate_controller = RateLimitController(min_request_interval=1.0)
    rate_controller._last_request_time = 1000.0

    # First call - should wait 1.0 seconds (because 0 seconds have passed
    # since the last request)
    rate_controller.wait_if_needed()
    mock_sleep.assert_called_with(1.0)

    # Second call - should wait 0.0 seconds (because 1.0 seconds have passed
    # since the last request, which is >= 1.0)
    mock_sleep.reset_mock()
    rate_controller.wait_if_needed()
    mock_sleep.assert_not_called()


if __name__ == "__main__":
    pytest.main()
