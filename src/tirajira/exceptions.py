"""
Module for custom exceptions in TiraJira.
"""


class TiraJiraError(Exception):
    """Base class for TiraJira exceptions."""

    pass


class TaskCreatorError(TiraJiraError):
    """Exception raised when task creation errors occur."""

    pass
