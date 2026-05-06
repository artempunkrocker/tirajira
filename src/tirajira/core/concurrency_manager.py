"""Module for managing concurrent processing of Jira issues."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from tirajira.logger import get_logger


class ConcurrencyManager:
    """
    Manages concurrent processing of Jira issues with different error
    handling strategies.

    This class handles processing of issues either sequentially or in
    parallel, with options to stop on error or continue processing
    despite errors.
    """

    def __init__(
        self,
        max_concurrent_requests: int = 10,
        verbose: bool = False,
        thread_pool_executor_cls: Type[ThreadPoolExecutor] = ThreadPoolExecutor,
    ):
        """
        Initializes the ConcurrencyManager.

        Args:
            max_concurrent_requests: Maximum number of concurrent requests.
                                     If <= 1, processing is sequential.
            verbose: Whether to enable verbose logging.
            thread_pool_executor_cls: ThreadPoolExecutor class to use for
                parallel processing.
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.verbose = verbose
        self.thread_pool_executor_cls = thread_pool_executor_cls
        self.logger = get_logger()
        if self.verbose:
            self.logger.set_verbose(True)

    def process(
        self,
        issues: List[Dict[Any, Any]],
        processor_func: Callable,
        stop_on_error: bool = False,
        verbose: bool = False,
        thread_pool_executor_cls: Optional[Type[ThreadPoolExecutor]] = None,
    ) -> Tuple[int, List[Optional[Dict[str, Any]]]]:
        """
        Processes issues with the appropriate strategy based on configuration.

        Args:
            issues: List of issues to process.
            processor_func: Function to process a single issue.
            stop_on_error: Whether to stop processing on error.
            verbose: Whether to enable verbose logging.
            thread_pool_executor_cls: ThreadPoolExecutor class to use for
                parallel processing.

        Returns:
            A tuple of the number of successfully processed issues and a list with
            processing details for each issue.
        """
        effective_verbose = verbose if verbose else self.verbose
        effective_thread_pool_executor_cls = (
            thread_pool_executor_cls
            if thread_pool_executor_cls
            else self.thread_pool_executor_cls
        )

        if effective_verbose != self.logger.verbose_mode:
            self.logger.set_verbose(effective_verbose)

        original_verbose = self.verbose
        original_thread_pool_executor_cls = self.thread_pool_executor_cls

        self.verbose = effective_verbose
        self.thread_pool_executor_cls = effective_thread_pool_executor_cls

        try:
            if self.max_concurrent_requests <= 1:
                # Sequential processing
                return self._process_sequential(issues, processor_func)
            else:
                # Parallel processing
                if stop_on_error:
                    return self._process_parallel_stop_on_error(issues, processor_func)
                else:
                    return self._process_parallel_continue_on_error(
                        issues, processor_func
                    )
        finally:
            self.verbose = original_verbose
            self.thread_pool_executor_cls = original_thread_pool_executor_cls

    def _process_sequential(
        self,
        issues: List[Dict[Any, Any]],
        processor_func: Callable,
    ) -> Tuple[int, List[Optional[Dict[str, Any]]]]:
        """
        Processes issues sequentially when max_concurrent_requests <= 1.

        Args:
            issues: List of issues to process.
            processor_func: Function to process a single issue.

        Returns:
            A tuple of the number of successfully processed issues and a list with
            processing details for each issue. On error, processing stops and
            only processed elements are returned.
        """
        successful_count = 0
        processing_details: List[Optional[Dict[str, Any]]] = []

        for i, issue_data in enumerate(issues):
            if self.verbose:
                self.logger.progress(f"Processing issue {i + 1}/{len(issues)}...")

            try:
                task_detail, success = processor_func(issue_data, i)

                if success:
                    successful_count += 1

                processing_details.append(task_detail)

                # Check for errors
                if self._should_stop_on_error(task_detail, success):
                    self.logger.error("Processing stopped due to error")
                    break

            except Exception as exc:
                task_detail = self._create_failure_task_detail(issue_data, i, exc)
                processing_details.append(task_detail)
                self.logger.error("Processing stopped due to error")
                break

        return successful_count, processing_details

    def _process_parallel_stop_on_error(
        self,
        issues: List[Dict[Any, Any]],
        processor_func: Callable,
    ) -> Tuple[int, List[Optional[Dict[str, Any]]]]:
        """
        Processes issues in parallel with immediate stopping on error.

        Args:
            issues: List of issues to process.
            processor_func: Function to process a single issue.

        Returns:
            A tuple of the number of successfully processed issues and a list with
            processing details for each issue. Unprocessed issues are represented
            as None.
        """
        successful_count = 0
        processing_details: List[Optional[Dict[str, Any]]] = [None] * len(issues)

        # Use the injected ThreadPoolExecutor with a limited number of threads
        with self.thread_pool_executor_cls(
            max_workers=self.max_concurrent_requests
        ) as executor:
            # Process issues in batches
            i = 0
            error_occurred = False

            while i < len(issues) and not error_occurred:
                # Determine the size of the current batch
                batch_end = min(i + self.max_concurrent_requests, len(issues))
                batch_size = batch_end - i

                # Process one issue at a time to stop immediately on error
                for j in range(batch_size):
                    if error_occurred:
                        # Do not process remaining issues in the batch
                        break

                    index = i + j
                    future = executor.submit(
                        self._process_with_index, processor_func, index, issues[index]
                    )

                    # Wait for the result immediately
                    try:
                        idx, task_detail, success = future.result()
                        processing_details[idx] = task_detail
                        if success:
                            successful_count += 1
                        # Check for errors to stop processing
                        if self._should_stop_on_error(task_detail, success):
                            self.logger.error("Processing stopped due to error")
                            error_occurred = True
                            # Leave unprocessed issues as None
                            break

                    except Exception as exc:
                        task_detail = self._create_failure_task_detail(
                            issues[index], index, exc
                        )
                        processing_details[index] = task_detail
                        self.logger.error("Processing stopped due to error")
                        error_occurred = True
                        # Leave unprocessed issues as None
                        break

                if not error_occurred:
                    i += batch_size

        return successful_count, processing_details

    def _process_parallel_continue_on_error(
        self,
        issues: List[Dict[Any, Any]],
        processor_func: Callable,
    ) -> Tuple[int, List[Optional[Dict[str, Any]]]]:
        """
        Processes issues in parallel and continues processing despite errors.

        Args:
            issues: List of issues to process.
            processor_func: Function to process a single issue.

        Returns:
            A tuple of the number of successfully processed issues and a list with
            processing details for each issue. Unprocessed issues are represented
            as None.
        """
        successful_count = 0
        processing_details: List[Optional[Dict[str, Any]]] = [None] * len(issues)

        # Use the injected ThreadPoolExecutor with a limited number of threads
        with self.thread_pool_executor_cls(
            max_workers=self.max_concurrent_requests
        ) as executor:
            # Process issues in batches
            i = 0

            while i < len(issues):
                # Determine the size of the current batch
                batch_end = min(i + self.max_concurrent_requests, len(issues))
                batch_size = batch_end - i

                # Process all issues in the batch in parallel
                futures = []
                for j in range(batch_size):
                    index = i + j
                    future = executor.submit(
                        self._process_with_index, processor_func, index, issues[index]
                    )
                    futures.append((index, future))

                # Wait for all results and store them at the correct indices
                for index, future in futures:
                    try:
                        idx, task_detail, success = future.result()
                        processing_details[idx] = task_detail
                        if success:
                            successful_count += 1
                    except Exception as exc:
                        task_detail = self._create_failure_task_detail(
                            issues[index], index, exc
                        )
                        processing_details[index] = task_detail

                i += batch_size

        return successful_count, processing_details

    def _process_with_index(self, processor_func, index, issue_data):
        """
        Helper method to process an issue with its index.

        Args:
            processor_func: Function to process a single issue.
            index: Index of the issue in the original list.
            issue_data: Issue data to process.

        Returns:
            A tuple of the index, task detail, and success flag.
        """
        try:
            task_detail, success = processor_func(issue_data, index)
            return index, task_detail, success
        except Exception as exc:
            task_detail = self._create_failure_task_detail(issue_data, index, exc)
            return index, task_detail, False

    def _should_stop_on_error(self, task_detail: Dict[str, Any], success: bool) -> bool:
        """
        Determines if processing should stop based on task result.

        Args:
            task_detail: Details of the task processing.
            success: Whether the task was processed successfully.

        Returns:
            True if processing should stop, False otherwise.
        """
        return not success or "error_message" in task_detail

    def _create_failure_task_detail(
        self, issue_data: Dict[Any, Any], index: int, exception: Exception
    ) -> Dict[str, Any]:
        """
        Creates a task detail dict for a failed task.

        Args:
            issue_data: Original issue data.
            index: Index of the issue.
            exception: Exception that occurred.

        Returns:
            Task detail dictionary with error information.
        """
        # Handle case where issue_data is not a dictionary
        if not isinstance(issue_data, dict):
            issue_summary = str(issue_data)
        else:
            issue_summary = (
                f"{issue_data.get('project', {}).get('key', 'Unknown')} - "
                f"{issue_data.get('summary', 'No summary')}"
            )

        return {
            "status": "failure",
            "issue_data": {} if not isinstance(issue_data, dict) else issue_data,
            "processed_at": datetime.now().isoformat(),
            "id": index,
            "error_message": str(exception),
            "issue_summary": issue_summary,
        }

    def set_thread_pool_executor_cls(self, cls: Type[ThreadPoolExecutor]) -> None:
        """
        Sets the ThreadPoolExecutor class to use for parallel processing.

        Args:
            cls: ThreadPoolExecutor class to use.
        """
        self.thread_pool_executor_cls = cls
