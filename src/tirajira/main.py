"""
Main script for automating Jira task creation.
Supports creating tasks from a list in a file (JSON/YAML/CSV/Excel).
"""

import sys
from typing import Optional

# Import necessary classes for compatibility with tests
from .commands.cli import main as cli_main
from .core.rate_limiter import RateLimiter
from .integrations.jira_client import JiraClient
from .logger import get_logger
from .processing.task_creator import TaskCreator


def create_tasks_from_file(
    file_path: str,
    max_concurrent_requests: int = 10,
    min_request_interval: float = 1.0,
    stop_on_error: bool = False,
    verbose: bool = False,
    report_file: Optional[str] = None,
) -> None:
    """
    Create tasks based on a list from a file.

    Args:
        file_path: Path to the file with tasks.
        max_concurrent_requests: Maximum number of concurrent requests.
        min_request_interval: Minimum interval between requests in seconds.
        stop_on_error: Stop processing when an error occurs.
        verbose: Verbose logging mode flag.
        report_file: Path to the report file (None - don't save report,
                    True - automatically generate filename,
                    str - use specified filename).
    """
    # Initialize logger
    logger = get_logger()
    logger.set_verbose(verbose)

    try:
        # Initialize Jira client
        jira_client = JiraClient(verbose=verbose)

        # Initialize rate limiter
        rate_limiter = RateLimiter(
            jira_client,
            max_concurrent_requests=max_concurrent_requests,
            min_request_interval=min_request_interval,
            stop_on_error=stop_on_error,
            verbose=verbose,
        )

        # Initialize task creator
        task_creator = TaskCreator(
            jira_client=jira_client, rate_limiter=rate_limiter, verbose=verbose
        )

        # Create tasks
        task_creator.create_from_file(
            file_path=file_path,
            max_concurrent_requests=max_concurrent_requests,
            min_request_interval=min_request_interval,
            stop_on_error=stop_on_error,
            verbose=verbose,
            report_file=report_file,
        )

    except Exception as e:
        logger.error(f"Error creating tasks: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    # Use the new CLI interface
    cli_main()


if __name__ == "__main__":
    main()
    sys.exit(0)  # Exit with code 0 if everything went successfully
