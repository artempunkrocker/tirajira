"""
Base class for TiraJira commands.
"""

from ..core.rate_limiter import RateLimiter
from ..integrations.jira_client import JiraClient
from ..logger import get_logger
from ..processing.task_creator import TaskCreator


class BaseCommand:
    """Base command class."""

    def __init__(self, args):
        self.args = args
        self.logger = get_logger()
        self.jira_client = None
        self.rate_limiter = None
        self.task_creator = None

    def execute(self):
        """Executes the command."""
        raise NotImplementedError("Method execute must be implemented in subclass.")

    def _initialize_services(self):
        """Initializes common Jira services."""
        verbose = getattr(self.args, "verbose", False)
        self.jira_client = JiraClient(verbose=verbose)

        self.rate_limiter = RateLimiter(
            self.jira_client,
            max_concurrent_requests=getattr(self.args, "max_concurrent_requests", 10),
            min_request_interval=getattr(self.args, "min_request_interval", 1),
            stop_on_error=getattr(self.args, "stop_on_error", False),
            verbose=verbose,
        )

        self.task_creator = TaskCreator(
            jira_client=self.jira_client,
            rate_limiter=self.rate_limiter,
            verbose=verbose,
        )

    def run(self):
        """
        Template method for executing the command.
        Initializes services and calls the execute method.
        """
        verbose = getattr(self.args, "verbose", False)
        self.logger.set_verbose(verbose)
        self._initialize_services()
        return self.execute()
