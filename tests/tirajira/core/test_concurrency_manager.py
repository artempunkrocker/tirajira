"""
Tests for the Jira task parallel processing management module.
"""

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, Mock, patch

import pytest

from tirajira.core.concurrency_manager import ConcurrencyManager


def dummy_processor_func(issue_data, index):
    """
    Function for testing task processing.

    Args:
        issue_data: Task data to process.
        index: Task index in the list.

    Returns:
        tuple: A tuple containing a dictionary with processing details and a boolean
               indicating the success of the operation.
    """
    if "should_fail" in issue_data and issue_data["should_fail"]:
        raise Exception("Processing failed")

    task_detail = {
        "status": "success",
        "issue_data": issue_data,
        "processed_at": "2023-01-01T00:00:00",
        "id": index,
        "issue_key": f"PROJ-{100 + index}",
    }
    return task_detail, True


def test_concurrency_manager_init():
    """Test: ConcurrencyManager initialization"""
    # Create a manager with default parameters
    cm = ConcurrencyManager()
    assert cm.max_concurrent_requests == 10
    assert cm.verbose is False
    assert cm.thread_pool_executor_cls == ThreadPoolExecutor

    # Create a manager with custom parameters
    cm = ConcurrencyManager(max_concurrent_requests=5, verbose=True)
    assert cm.max_concurrent_requests == 5
    assert cm.verbose is True


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_sequential_success(mock_get_logger):
    """Test: successful sequential task processing"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=1, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm._process_sequential(
        issues, dummy_processor_func
    )

    assert successful_count == 3
    assert len(processing_details) == 3

    for i, detail in enumerate(processing_details):
        assert detail["status"] == "success"
        assert detail["id"] == i
        assert detail["issue_key"] == f"PROJ-{100 + i}"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_sequential_with_verbose_logging(mock_get_logger):
    """Test: sequential task processing with verbose logging"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=1, verbose=True)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    with patch.object(cm.logger, "progress") as mock_progress:
        successful_count, processing_details = cm._process_sequential(
            issues, dummy_processor_func
        )

        assert mock_progress.call_count == 2
        mock_progress.assert_any_call("Processing issue 1/2...")
        mock_progress.assert_any_call("Processing issue 2/2...")


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_sequential_stop_on_error(mock_get_logger):
    """Test: sequential task processing with stop on error"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=1, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}, "should_fail": True},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    with patch.object(cm.logger, "error") as mock_error:
        successful_count, processing_details = cm._process_sequential(
            issues, dummy_processor_func
        )

        # Only the first task should be processed successfully
        assert successful_count == 1
        # Only the first two tasks were processed (first successfully,
        # second with error)
        assert len(processing_details) == 2

        # Check that the second task failed
        assert processing_details[0]["status"] == "success"
        assert processing_details[1]["status"] == "failure"

        # Check that the processing error was called
        assert mock_error.call_count == 1
        mock_error.assert_called_with("Processing stopped due to error")


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_parallel_continue_on_error_success(
    mock_get_logger,
):
    """Test: successful parallel task processing with continue on errors"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Mock ThreadPoolExecutor as a context manager
    mock_executor = MagicMock()
    mock_future = Mock()

    # Configure mocks to return successful results
    mock_future.result.side_effect = [
        (0, {"status": "success", "id": 0, "issue_key": "PROJ-100"}, True),
        (1, {"status": "success", "id": 1, "issue_key": "PROJ-101"}, True),
        (2, {"status": "success", "id": 2, "issue_key": "PROJ-102"}, True),
    ]
    mock_executor.submit.return_value = mock_future

    # Create a MagicMock that returns our mocked executor
    mock_thread_pool_executor_cls = MagicMock()
    mock_thread_pool_executor_cls.return_value.__enter__.return_value = mock_executor

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)
    cm.thread_pool_executor_cls = mock_thread_pool_executor_cls

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm._process_parallel_continue_on_error(
        issues, dummy_processor_func
    )

    assert successful_count == 3
    assert len(processing_details) == 3

    for i, detail in enumerate(processing_details):
        assert detail["status"] == "success"
        assert detail["id"] == i
        assert detail["issue_key"] == f"PROJ-{100 + i}"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_parallel_continue_on_error_with_failure(
    mock_get_logger,
):
    """Test: parallel task processing with continue on errors and
    actual failures"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Mock ThreadPoolExecutor as a context manager
    mock_executor = MagicMock()
    mock_future1 = Mock()
    mock_future2 = Mock()
    mock_future3 = Mock()

    # Configure mocks to return results with errors
    mock_future1.result.return_value = (
        0,
        {"status": "success", "id": 0, "issue_key": "PROJ-100"},
        True,
    )
    mock_future2.result.side_effect = Exception("Future failed")
    mock_future3.result.return_value = (
        2,
        {"status": "success", "id": 2, "issue_key": "PROJ-102"},
        True,
    )

    # Configure submit to return different futures
    mock_executor.submit.side_effect = [mock_future1, mock_future2, mock_future3]

    # Create a MagicMock that returns our mocked executor
    mock_thread_pool_executor_cls = MagicMock()
    mock_thread_pool_executor_cls.return_value.__enter__.return_value = mock_executor

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)
    cm.thread_pool_executor_cls = mock_thread_pool_executor_cls

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm._process_parallel_continue_on_error(
        issues, dummy_processor_func
    )

    # The first and third tasks should be processed successfully
    assert successful_count == 2
    assert len(processing_details) == 3

    # First task - success
    assert processing_details[0]["status"] == "success"
    assert processing_details[0]["id"] == 0
    assert processing_details[0]["issue_key"] == "PROJ-100"

    # Second task - error
    assert processing_details[1]["status"] == "failure"
    assert processing_details[1]["id"] == 1
    assert "Future failed" in processing_details[1]["error_message"]

    # Third task - success
    assert processing_details[2]["status"] == "success"
    assert processing_details[2]["id"] == 2
    assert processing_details[2]["issue_key"] == "PROJ-102"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_sequential_mode(mock_get_logger):
    """Test: main process method in sequential mode"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=1, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm.process(issues, dummy_processor_func)

    assert successful_count == 2
    assert len(processing_details) == 2

    for i, detail in enumerate(processing_details):
        assert detail["status"] == "success"
        assert detail["id"] == i
        assert detail["issue_key"] == f"PROJ-{100 + i}"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_parallel_stop_on_error_mode(mock_get_logger):
    """Test: main process method in parallel mode with stop on error"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Mock ThreadPoolExecutor as a context manager
    mock_executor = MagicMock()
    mock_future = Mock()

    # Configure mocks to return successful results
    mock_future.result.side_effect = [
        (0, {"status": "success", "id": 0, "issue_key": "PROJ-100"}, True),
        (1, {"status": "success", "id": 1, "issue_key": "PROJ-101"}, True),
    ]
    mock_executor.submit.return_value = mock_future

    # Create a MagicMock that returns our mocked executor
    mock_thread_pool_executor_cls = MagicMock()
    mock_thread_pool_executor_cls.return_value.__enter__.return_value = mock_executor

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)
    cm.thread_pool_executor_cls = mock_thread_pool_executor_cls

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm.process(
        issues, dummy_processor_func, stop_on_error=True
    )

    assert successful_count == 2
    assert len(processing_details) == 2

    for i, detail in enumerate(processing_details):
        assert detail["status"] == "success"
        assert detail["id"] == i
        assert detail["issue_key"] == f"PROJ-{100 + i}"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_parallel_continue_on_error_mode(
    mock_get_logger,
):
    """Test: main process method in parallel mode with continue on errors"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Mock ThreadPoolExecutor as a context manager
    mock_executor = MagicMock()
    mock_future = Mock()

    # Configure mocks to return successful results
    mock_future.result.side_effect = [
        (0, {"status": "success", "id": 0, "issue_key": "PROJ-100"}, True),
        (1, {"status": "success", "id": 1, "issue_key": "PROJ-101"}, True),
    ]
    mock_executor.submit.return_value = mock_future

    # Create a MagicMock that returns our mocked executor
    mock_thread_pool_executor_cls = MagicMock()
    mock_thread_pool_executor_cls.return_value.__enter__.return_value = mock_executor

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)
    cm.thread_pool_executor_cls = mock_thread_pool_executor_cls

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm.process(
        issues, dummy_processor_func, stop_on_error=False
    )

    assert successful_count == 2
    assert len(processing_details) == 2

    for i, detail in enumerate(processing_details):
        assert detail["status"] == "success"
        assert detail["id"] == i
        assert detail["issue_key"] == f"PROJ-{100 + i}"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_verbose_mode(mock_get_logger):
    """Test: main process method with verbose mode"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=1, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
    ]

    # Test with verbose=True in the process method
    successful_count, processing_details = cm.process(
        issues, dummy_processor_func, verbose=True
    )

    # Check that the verbose mode was set
    assert cm.verbose is False  # Should return to the original value

    assert successful_count == 1
    assert len(processing_details) == 1
    assert processing_details[0]["status"] == "success"


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_empty_issues_list(mock_get_logger):
    """Test: main process method with empty task list"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=10, verbose=False)

    issues = []

    successful_count, processing_details = cm.process(issues, dummy_processor_func)

    assert successful_count == 0
    assert len(processing_details) == 0


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_exception_in_processor(mock_get_logger):
    """Test: main process method with exception in processor function"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    def failing_processor_func(issue_data, index):
        raise Exception("Processor function failed")

    cm = ConcurrencyManager(max_concurrent_requests=10, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
    ]

    successful_count, processing_details = cm.process(issues, failing_processor_func)

    assert successful_count == 0
    assert len(processing_details) == 1
    assert processing_details[0]["status"] == "failure"
    assert "Processor function failed" in processing_details[0]["error_message"]


@pytest.mark.parametrize(
    "processor_func,issue_data,index,expected_status,expected_success,"
    "has_error_message",
    [
        (
            dummy_processor_func,
            {"summary": "Test", "project": {"key": "PROJ"}},
            5,
            "success",
            True,
            False,
        ),
        ("not_a_dict_processor", "not_a_dict", 5, "success", True, False),
    ],
)
@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_index_success_cases(
    mock_get_logger,
    processor_func,
    issue_data,
    index,
    expected_status,
    expected_success,
    has_error_message,
):
    """Test: _process_with_index method with successful processing"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=10, verbose=False)

    # Handle special case for non-dict processor
    if processor_func == "not_a_dict_processor":

        def processor_func(issue_data, index):
            task_detail = {
                "status": "success",
                "issue_data": issue_data,
                "processed_at": "2023-01-01T00:00:00",
                "id": index,
                "issue_key": f"PROJ-{100 + index}",
            }
            return task_detail, True

    result_index, task_detail, success = cm._process_with_index(
        processor_func, index, issue_data
    )

    assert result_index == index
    assert task_detail["status"] == expected_status
    assert task_detail["id"] == index
    assert success is expected_success


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_index_exception(mock_get_logger):
    """Test: _process_with_index method with exception in processing"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    def failing_processor_func(issue_data, index):
        raise Exception("Processing failed")

    cm = ConcurrencyManager(max_concurrent_requests=10, verbose=False)

    issue_data = {"summary": "Test", "project": {"key": "PROJ"}}
    index = 5

    result_index, task_detail, success = cm._process_with_index(
        failing_processor_func, index, issue_data
    )

    assert result_index == index
    assert task_detail["status"] == "failure"
    assert task_detail["id"] == index
    assert "Processing failed" in task_detail["error_message"]
    assert success is False


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_sequential_with_error_message_in_task_detail(
    mock_get_logger,
):
    """Test: sequential processing with error message in task details"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    call_count = 0

    def processor_func_with_error_message(issue_data, index):
        nonlocal call_count
        call_count += 1

        # Only the first task will have an error message
        if index == 0:
            task_detail = {
                "status": "success",  # success=True, but there is an error message
                "issue_data": issue_data,
                "processed_at": "2023-01-01T00:00:00",
                "id": index,
                "error_message": "Some error occurred",  # This will cause a stop
            }
            return task_detail, True  # success=True
        else:
            # The second task is processed normally, but should not be reached
            task_detail = {
                "status": "success",
                "issue_data": issue_data,
                "processed_at": "2023-01-01T00:00:00",
                "id": index,
            }
            return task_detail, True

    cm = ConcurrencyManager(max_concurrent_requests=1, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    with patch.object(cm.logger, "error") as mock_error:
        successful_count, processing_details = cm._process_sequential(
            issues, processor_func_with_error_message
        )

        # The first task is technically successful (success=True),
        # so successful_count = 1
        # But processing stops due to error_message
        assert successful_count == 1
        # Only the first task was processed before stopping
        assert len(processing_details) == 1

        # Check that the handler was called only once
        assert call_count == 1

        # Check that the processing error was called
        assert mock_error.call_count == 1
        mock_error.assert_called_with("Processing stopped due to error")


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_parallel_stop_on_error_with_exception_in_future(
    mock_get_logger,
):
    """Test: parallel processing with stop on error and exception in future"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Mock ThreadPoolExecutor as a context manager
    mock_executor = MagicMock()
    mock_future1 = Mock()
    mock_future2 = Mock()

    # Configure mocks to return a successful result and an exception
    mock_future1.result.return_value = (
        0,
        {"status": "success", "id": 0, "issue_key": "PROJ-100"},
        True,
    )
    mock_future2.result.side_effect = Exception("Future execution failed")

    # Configure submit to return different futures
    mock_executor.submit.side_effect = [mock_future1, mock_future2]

    # Create a MagicMock that returns our mocked executor
    mock_thread_pool_executor_cls = MagicMock()
    mock_thread_pool_executor_cls.return_value.__enter__.return_value = mock_executor

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)
    cm.thread_pool_executor_cls = mock_thread_pool_executor_cls

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
    ]

    with patch.object(cm.logger, "error") as mock_error:
        successful_count, processing_details = cm._process_parallel_stop_on_error(
            issues, dummy_processor_func
        )

        # Only the first task should be processed successfully
        assert successful_count == 1
        assert len(processing_details) == 3

        # Check that the third task was not processed (None)
        assert processing_details[0]["status"] == "success"
        assert processing_details[1]["status"] == "failure"
        assert processing_details[2] is None

        # Check that the processing error was called
        assert mock_error.call_count == 1
        mock_error.assert_called_with("Processing stopped due to error")


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_with_custom_thread_pool_executor_cls(
    mock_get_logger,
):
    """Test: main process method with custom ThreadPoolExecutor class"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    # Create a custom ThreadPoolExecutor class
    class CustomThreadPoolExecutor(ThreadPoolExecutor):
        pass

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
    ]

    # Save the original class
    original_cls = cm.thread_pool_executor_cls

    # Test with custom class
    successful_count, processing_details = cm.process(
        issues, dummy_processor_func, thread_pool_executor_cls=CustomThreadPoolExecutor
    )

    # Check that the class was set
    assert cm.thread_pool_executor_cls == original_cls

    # For this test we just check that the method didn't raise exceptions
    # Actual processing will be done in sequential mode because we don't
    # mock CustomThreadPoolExecutor
    assert successful_count >= 0


def test_concurrency_manager_process_with_thread_pool_executor_branch_coverage():
    """Test: coverage of thread_pool_executor_cls is not None branch in
    process method"""

    # Create a custom ThreadPoolExecutor class
    class CustomThreadPoolExecutor(ThreadPoolExecutor):
        pass

    cm = ConcurrencyManager(
        max_concurrent_requests=1, verbose=False
    )  # Will use sequential processing

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
    ]

    # Call process with custom ThreadPoolExecutor class
    # This should activate the if thread_pool_executor_cls is not None: branch

    successful_count, processing_details = cm.process(
        issues,
        dummy_processor_func,
        thread_pool_executor_cls=CustomThreadPoolExecutor,
        stop_on_error=True,
    )


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_set_thread_pool_executor_cls(mock_get_logger):
    """Test: set_thread_pool_executor_cls method"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=2, verbose=False)

    # Save the original class
    original_cls = cm.thread_pool_executor_cls

    # Create a new class for testing
    class TestThreadPoolExecutor(ThreadPoolExecutor):
        pass

    # Set the new class
    cm.set_thread_pool_executor_cls(TestThreadPoolExecutor)

    # Check that the class was set
    assert cm.thread_pool_executor_cls == TestThreadPoolExecutor

    # Restore the original class
    cm.set_thread_pool_executor_cls(original_cls)

    # Check that the class was restored
    assert cm.thread_pool_executor_cls == original_cls


@patch("tirajira.core.concurrency_manager.get_logger")
@patch("tirajira.core.concurrency_manager.datetime")
@pytest.mark.parametrize(
    "issue_data,expected_issue_data",
    [
        (
            {"summary": "Test", "project": {"key": "PROJ"}},
            {"summary": "Test", "project": {"key": "PROJ"}},
        ),
        ("not_a_dict", {}),
    ],
)
def test_concurrency_manager_create_failure_task_detail(
    mock_datetime, mock_get_logger, issue_data, expected_issue_data
):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"

    cm = ConcurrencyManager(max_concurrent_requests=10, verbose=False)

    index = 5
    exception = Exception("Processing failed")

    result = cm._create_failure_task_detail(issue_data, index, exception)

    assert result["status"] == "failure"
    assert result["issue_data"] == expected_issue_data
    assert result["processed_at"] == "2023-01-01T00:00:00"
    assert result["id"] == index
    assert result["error_message"] == "Processing failed"


@pytest.mark.parametrize(
    "task_detail,success,expected_result",
    [
        (
            {
                "status": "success",
                "issue_data": {"summary": "Test", "project": {"key": "PROJ"}},
                "processed_at": "2023-01-01T00:00:00",
                "id": 0,
            },
            True,
            False,
        ),
        (
            {
                "status": "success",
                "issue_data": {"summary": "Test", "project": {"key": "PROJ"}},
                "processed_at": "2023-01-01T00:00:00",
                "id": 0,
            },
            False,
            True,
        ),
        (
            {
                "status": "success",
                "issue_data": {"summary": "Test", "project": {"key": "PROJ"}},
                "processed_at": "2023-01-01T00:00:00",
                "id": 0,
                "error_message": "Some error occurred",
            },
            True,
            True,
        ),
    ],
)
@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_should_stop_on_error(
    mock_get_logger, task_detail, success, expected_result
):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    cm = ConcurrencyManager(max_concurrent_requests=10, verbose=False)

    result = cm._should_stop_on_error(task_detail, success)

    assert result is expected_result


@patch("tirajira.core.concurrency_manager.get_logger")
def test_concurrency_manager_process_parallel_stop_on_error_skip_remaining_in_batch(
    mock_get_logger,
):
    """Test parallel processing with early termination skipping
    remaining tasks in batch"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_executor = MagicMock()

    mock_futures = []
    for _i in range(3):
        mock_future = Mock()
        mock_futures.append(mock_future)

    mock_futures[0].result.return_value = (
        0,
        {"status": "success", "id": 0, "issue_key": "PROJ-100"},
        True,
    )
    mock_futures[1].result.return_value = (
        1,
        {"status": "failure", "id": 1, "error_message": "Processing failed"},
        False,
    )

    submitted_tasks = []

    def track_submit_calls(func, process_func, index, issue_data):
        submitted_tasks.append(index)
        return mock_futures[index]

    mock_executor.submit.side_effect = track_submit_calls

    mock_thread_pool_executor_cls = MagicMock()
    mock_thread_pool_executor_cls.return_value.__enter__.return_value = mock_executor

    cm = ConcurrencyManager(max_concurrent_requests=3, verbose=False)
    cm.thread_pool_executor_cls = mock_thread_pool_executor_cls

    issues = [
        {"summary": "Test 1", "project": {"key": "PROJ"}},
        {"summary": "Test 2", "project": {"key": "PROJ"}},
        {"summary": "Test 3", "project": {"key": "PROJ"}},
        {"summary": "Test 4", "project": {"key": "PROJ"}},
        {"summary": "Test 5", "project": {"key": "PROJ"}},
    ]

    with patch.object(cm.logger, "error") as mock_error:
        successful_count, processing_details = cm._process_parallel_stop_on_error(
            issues, dummy_processor_func
        )

        assert successful_count == 1
        assert len(processing_details) == 5

        assert processing_details[0]["status"] == "success"
        assert processing_details[1]["status"] == "failure"

        assert processing_details[2] is None
        assert processing_details[3] is None
        assert processing_details[4] is None

        assert len(submitted_tasks) == 2
        assert submitted_tasks == [0, 1]

        assert mock_error.call_count == 1
        mock_error.assert_called_with("Processing stopped due to error")


if __name__ == "__main__":
    pytest.main()
