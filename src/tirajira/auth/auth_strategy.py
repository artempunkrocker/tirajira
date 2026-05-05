"""
Module of authentication strategies for Jira API.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from jira import JIRA


class AuthStrategy(ABC):
    """Abstract class for authentication strategies."""

    @abstractmethod
    def authenticate(self) -> JIRA:
        """Authenticates and returns JIRA client."""
        pass

    @abstractmethod
    def get_auth_params(self) -> Dict[str, Any]:
        """Returns authentication parameters for logging (without secrets)."""
        pass


class BasicAuthStrategy(AuthStrategy):
    """Basic authentication strategy."""

    def __init__(self, server: str, email: str, api_token: str):
        self.server = server
        self.email = email
        self.api_token = api_token

    def authenticate(self) -> JIRA:
        """Authenticates and returns JIRA client with basic authentication."""
        return JIRA(
            server=self.server,
            basic_auth=(self.email, self.api_token),
        )

    def get_auth_params(self) -> Dict[str, Any]:
        """Returns authentication parameters for logging."""
        return {"server": self.server, "email": self.email, "auth_type": "basic_auth"}


class PatAuthStrategy(AuthStrategy):
    """Authentication strategy via Personal Access Token."""

    def __init__(self, server: str, pat_token: str):
        self.server = server
        self.pat_token = pat_token

    def authenticate(self) -> JIRA:
        """Authenticates and returns JIRA client with PAT authentication."""
        return JIRA(
            server=self.server,
            token_auth=self.pat_token,
        )

    def get_auth_params(self) -> Dict[str, Any]:
        """Returns authentication parameters for logging."""
        return {"server": self.server, "auth_type": "pat_auth"}
