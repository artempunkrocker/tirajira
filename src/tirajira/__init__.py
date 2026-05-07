"""
TiraJira - a tool for automating mass task creation in Jira.

The module allows creating tasks in Jira from JSON, YAML, CSV, or Excel files.
Supports linking tasks to epics and logging the task creation process.
"""

__version__ = "1.1.3"

from .commands import BaseCommand, ExtractFailedCommand, ImportCommand, ResumeCommand

# Import main classes and functions for convenience of use
from .commands.argument_parser import ArgumentParser
from .core.concurrency_manager import ConcurrencyManager
from .core.rate_limit_controller import RateLimitController
from .core.rate_limiter import RateLimiter
from .file_loaders import create_file_loader
from .integrations.jira_client import JiraClient
from .integrations.jira_client_interface import JiraClientInterface
from .main import create_tasks_from_file
from .processing.report_generator import ReportGenerator
from .processing.task_creator import TaskCreator
from .processing.task_processor import TaskProcessor

__all__ = [
    "ArgumentParser",
    "ConcurrencyManager",
    "JiraClient",
    "JiraClientInterface",
    "RateLimiter",
    "RateLimitController",
    "ReportGenerator",
    "TaskCreator",
    "TaskProcessor",
    "create_file_loader",
    "create_tasks_from_file",
    "BaseCommand",
    "ImportCommand",
    "ExtractFailedCommand",
    "ResumeCommand",
]
