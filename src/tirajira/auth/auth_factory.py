"""
Factory for creating authentication strategies.
"""

import os

from .auth_strategy import AuthStrategy, BasicAuthStrategy, PatAuthStrategy


class AuthFactory:
    """Factory for creating authentication strategies."""

    @staticmethod
    def create_auth_strategy() -> AuthStrategy:
        """
        Creates authentication strategy based on environment variables.

        Returns:
            AuthStrategy: Authentication strategy

        Raises:
            ValueError: If strategy creation failed due to missing
                        required environment variables
        """
        # Check which authentication mode to use
        pat_token = os.getenv("JIRA_PAT_TOKEN")

        if pat_token:
            # Use token authentication (Personal Access Token)
            return AuthFactory._create_pat_strategy(pat_token)
        else:
            # Use basic authentication (backward compatibility)
            return AuthFactory._create_basic_auth_strategy()

    @staticmethod
    def _create_pat_strategy(pat_token: str) -> PatAuthStrategy:
        """Creates PAT authentication strategy."""
        jira_server = os.getenv("JIRA_SERVER")
        if not jira_server:
            raise ValueError("JIRA_SERVER is required for PAT authentication")

        return PatAuthStrategy(jira_server, pat_token)

    @staticmethod
    def _create_basic_auth_strategy() -> BasicAuthStrategy:
        """Creates basic authentication strategy."""
        jira_server = os.getenv("JIRA_SERVER")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_api_token = os.getenv("JIRA_API_TOKEN")

        if not jira_server:
            raise ValueError("JIRA_SERVER is required for basic authentication")
        if not jira_email:
            raise ValueError("JIRA_EMAIL is required for basic authentication")
        if not jira_api_token:
            raise ValueError("JIRA_API_TOKEN is required for basic authentication")

        return BasicAuthStrategy(jira_server, jira_email, jira_api_token)
