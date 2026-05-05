"""
Utility for validating JIRA link types with caching and error handling.
"""

import time
from typing import Optional, Set

from ..integrations.jira_client_interface import JiraClientInterface
from ..logger import get_logger


class LinkTypeValidator:
    """Validates link types against JIRA instance or common defaults with caching."""

    # Common default link types as fallback
    COMMON_LINK_TYPES = {
        "Blocks",
        "Relates",
        "Clones",
        "Duplicate",
        "Depends",
        "Parent",
        "Child",
        "Is Blocked By",
        "Is Related To",
        "Is Cloned By",
        "Is Duplicate Of",
        "Is Dependent On",
    }

    def __init__(self, jira_client: JiraClientInterface, cache_ttl: int = 300):
        """
        Initialize the LinkTypeValidator.

        Args:
            jira_client: Jira client instance for fetching valid link types
            cache_ttl: Time-to-live for cached link types in seconds
                       (default: 5 minutes)
        """
        self.jira_client = jira_client
        self.cache_ttl = cache_ttl
        self.logger = get_logger()
        self._cache_timestamp = 0
        self._cached_link_types: Optional[Set[str]] = None

    def _get_valid_link_types(self) -> Set[str]:
        """
        Retrieve valid link types from JIRA or fallback to defaults.

        Returns:
            Set of valid link type names
        """
        current_time = time.time()

        # Check if cache is still valid
        if (
            self._cached_link_types is not None
            and current_time - self._cache_timestamp < self.cache_ttl
        ):
            return self._cached_link_types

        # Try to fetch from JIRA
        try:
            link_types = self.jira_client.get_issue_link_types()
            if link_types:
                self._cached_link_types = set(link_types)
                self._cache_timestamp = current_time
                self.logger.debug(f"Retrieved {len(link_types)} link types from JIRA")
                return self._cached_link_types
        except Exception as e:
            self.logger.debug(f"Error fetching link types from JIRA: {str(e)}")

        # Fallback to common defaults
        self.logger.debug("Using common default link types as fallback")
        self._cached_link_types = self.COMMON_LINK_TYPES.copy()
        self._cache_timestamp = current_time
        return self._cached_link_types

    def is_valid_link_type(self, link_type: str) -> bool:
        """
        Validate if a link type is valid.

        Args:
            link_type: Link type name to validate

        Returns:
            True if link type is valid, False otherwise
        """
        if not link_type:
            return False

        valid_types = self._get_valid_link_types()
        is_valid = link_type in valid_types

        if not is_valid:
            self.logger.debug(f"Invalid link type: {link_type}")

        return is_valid
