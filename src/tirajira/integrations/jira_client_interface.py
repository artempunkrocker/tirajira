"""
Module with interface for Jira API client.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class JiraClientInterface(ABC):
    """Abstract class for interacting with the Jira API."""

    @abstractmethod
    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creating a single issue in Jira.

        Args:
            issue_data: Dictionary with data for creating an issue. Should contain
                required fields for project, issue type, and summary, and may also
                contain additional fields such as description, priority,
                assignee, etc.

        Returns:
            dict: Result of the issue creation operation.

            In case of success contains:
                success (bool): True if the issue was successfully created.
                issue_key (str): Key of the created issue.

            In case of error contains:
                success (bool): False if an error occurred while creating the issue.
                error (str): Error message.
        """
        pass

    @abstractmethod
    def link_to_epic(self, issue_key: str, epic_key: str) -> Dict[str, Any]:
        """
        Linking an issue to an epic.

        Args:
            issue_key: Key of the issue to link to the epic.
            epic_key: Key of the epic to link the issue to.

        Returns:
            dict: Result of the issue-to-epic linking operation.

            In case of success contains:
                success (bool): True if the issue was successfully linked to the epic.

            In case of error contains:
                success (bool): False if an error occurred while linking
                    the issue to the epic.
                error (str): Error message.
        """
        pass

    @abstractmethod
    def create_issue_link(
        self, link_type: str, inward_issue: str, outward_issue: str
    ) -> Dict[str, Any]:
        """
        Creating a link between two issues.

        Args:
            link_type: Type of link between issues.
            inward_issue: Key of the issue that will be linked as inward.
            outward_issue: Key of the issue that will be linked as outward.

        Returns:
            dict: Result of the link creation operation between issues.

            In case of success contains:
                success (bool): True if the link was successfully created.

            In case of error contains:
                success (bool): False if an error occurred while creating the link.
                error (str): Error message.
        """
        pass

    @abstractmethod
    def get_issue_link_types(self) -> List[str]:
        """
        Getting a list of available link types between issues.

        Returns:
            List[str]: List of available link types between issues.
        """
        pass
