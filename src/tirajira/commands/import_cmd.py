"""
Command to import tasks from a file.
"""

from .base import BaseCommand
from .exception_handler import handle_exceptions


class ImportCommand(BaseCommand):
    """Command to import tasks from a file."""

    @handle_exceptions
    def execute(self):
        """Executes importing tasks from a file."""
        # Create tasks with specified parameters
        self.task_creator.create_from_file(
            file_path=self.args.file,
            max_concurrent_requests=self.args.max_concurrent_requests,
            min_request_interval=self.args.min_request_interval,
            stop_on_error=self.args.stop_on_error,
            verbose=self.args.verbose,
            report_file=self.args.report,
        )
