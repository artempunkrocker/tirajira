"""
Module for limiting the frequency of requests to the Jira API.
"""

import time
from concurrent.futures import ThreadPoolExecutor as ThreadPoolExecutorImport
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple, Type

from ..integrations.jira_client_interface import JiraClientInterface
from ..logger import get_logger
from ..processing.task_processor import TaskProcessor
from .concurrency_manager import ConcurrencyManager
from .rate_limit_controller import RateLimitController

# This alias allows tests to patch ThreadPoolExecutor in this module
ThreadPoolExecutor = ThreadPoolExecutorImport


class RateLimiter:
    """Rate limiter for Jira API requests."""

    def __init__(
        self,
        jira_client: JiraClientInterface,
        max_concurrent_requests: int = 10,
        min_request_interval: float = 1,
        stop_on_error: bool = False,
        verbose: bool = False,
    ) -> None:
        self.jira_client = jira_client
        self.max_concurrent_requests = max_concurrent_requests
        self.min_request_interval = min_request_interval
        self.stop_on_error = stop_on_error
        self.verbose = verbose
        self.logger = get_logger()

        self._last_request_time = 0.0
        self._lock = Lock()

        self.rate_controller = RateLimitController(min_request_interval)
        self.task_processor = TaskProcessor(jira_client)
        self.concurrency_manager = ConcurrencyManager(
            max_concurrent_requests=max_concurrent_requests, verbose=verbose
        )

    def _resolve_processing_parameters(
        self,
        max_concurrent_requests: Optional[int],
        min_request_interval: Optional[float],
        stop_on_error: Optional[bool],
        verbose: Optional[bool],
    ) -> Dict[str, Any]:
        """Resolve actual parameter values for processing."""
        actual_max_concurrent_requests = (
            max_concurrent_requests
            if max_concurrent_requests is not None
            else self.max_concurrent_requests
        )
        actual_min_request_interval = (
            min_request_interval
            if min_request_interval is not None
            else self.min_request_interval
        )
        actual_stop_on_error = (
            stop_on_error if stop_on_error is not None else self.stop_on_error
        )
        actual_verbose = verbose if verbose is not None else self.verbose

        return {
            "max_concurrent_requests": actual_max_concurrent_requests,
            "min_request_interval": actual_min_request_interval,
            "stop_on_error": actual_stop_on_error,
            "verbose": actual_verbose,
        }

    def process(
        self,
        issues: List[Dict[Any, Any]],
        max_concurrent_requests: Optional[int] = None,
        min_request_interval: Optional[float] = None,
        stop_on_error: Optional[bool] = None,
        verbose: Optional[bool] = None,
        thread_pool_executor_cls: Optional[Type[ThreadPoolExecutor]] = None,
    ) -> Tuple[int, List[Optional[Dict[str, Any]]]]:
        """
        Processes a list of issues with request rate limiting and returns
        the number of successfully created issues and processing details.

        Args:
            issues: List of issues to process.
            max_concurrent_requests: Maximum number of concurrent
                                     requests (if None, the value from
                                     the constructor is used).
            min_request_interval: Minimum interval between requests (if
                                  None, the value from the constructor is used).
            stop_on_error: Stop processing on error (if None,
                           the value from the constructor is used).
            verbose: Verbose mode (if None, the value from
                     the constructor is used).
            thread_pool_executor_cls: ThreadPoolExecutor class to use
                                      (for testing).

        Returns:
            A tuple of the number of successfully created issues and a list with
            processing details for each issue. For unprocessed issues due to errors
            when using stop_on_error=True, None values are returned.
        """
        actual_params = self._resolve_processing_parameters(
            max_concurrent_requests, min_request_interval, stop_on_error, verbose
        )

        self.logger.set_verbose(actual_params["verbose"])
        if hasattr(self.jira_client, "logger") and self.jira_client.logger is not None:
            self.jira_client.logger.set_verbose(actual_params["verbose"])

        self.rate_controller.update_min_request_interval(
            actual_params["min_request_interval"]
        )
        self.concurrency_manager.max_concurrent_requests = actual_params[
            "max_concurrent_requests"
        ]
        self.concurrency_manager.verbose = actual_params["verbose"]

        def processor_func(
            issue_data: Dict[Any, Any], issue_index: int
        ) -> Tuple[Dict[str, Any], bool]:
            return self.task_processor.process_single_issue(
                issue_data, issue_index, self.rate_controller
            )

        # Handle backward compatibility for tests that patch ThreadPoolExecutor
        # in this module
        if (
            thread_pool_executor_cls is None
            and ThreadPoolExecutor is not ThreadPoolExecutorImport
        ):
            thread_pool_executor_cls = ThreadPoolExecutor

        successful_count, processing_details = self.concurrency_manager.process(
            issues=issues,
            processor_func=processor_func,
            stop_on_error=actual_params["stop_on_error"],
            verbose=actual_params["verbose"],
            thread_pool_executor_cls=thread_pool_executor_cls,
        )

        # Return the processing details as-is to maintain backward compatibility
        # with the tests, which expect None values for unprocessed items when
        # stop_on_error=True.
        return successful_count, processing_details

    def _wait_if_needed(self) -> None:
        if self.min_request_interval <= 0:
            return

        with self._lock:
            current_time = time.time()
            time_since_last_request = current_time - self._last_request_time
            if time_since_last_request < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last_request
                time.sleep(sleep_time)
                self._last_request_time = time.time()
            else:
                self._last_request_time = current_time
