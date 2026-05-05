"""
Module for authentication in Jira API.
"""

import logging
from typing import Optional

from jira import JIRA

from .auth_factory import AuthFactory
from .auth_strategy import AuthStrategy

logger = logging.getLogger(__name__)


class JiraAuthenticator:
    """Authenticator for Jira API."""

    def __init__(self, auth_strategy: Optional[AuthStrategy] = None):
        """
        Initializes the authenticator.

        Args:
            auth_strategy: Authentication strategy. If not specified, will be
                           created through factory.
        """
        self.auth_strategy = auth_strategy or AuthFactory.create_auth_strategy()

    def authenticate(self) -> JIRA:
        """
        Authenticates and returns JIRA client.

        Returns:
            JIRA: Authenticated JIRA client

        Raises:
            Exception: If authentication failed
        """
        try:
            auth_params = self.auth_strategy.get_auth_params()
            logger.info(f"Authentication in Jira: {auth_params}")
            jira_client = self.auth_strategy.authenticate()
            logger.info("Successful authentication in Jira")
            return jira_client
        except Exception as e:
            logger.error(f"Error authentication in Jira: {e}")
            raise
