"""
Module for working with Jira API.
"""

from typing import Any, Dict, List, Optional

from jira import JIRA
from jira.exceptions import JIRAError

from ..auth.jira_authenticator import JiraAuthenticator
from ..logger import get_logger
from .jira_client_interface import JiraClientInterface


class JiraClient(JiraClientInterface):
    """Client for interacting with Jira API."""

    def __init__(self, jira: Optional[JIRA] = None, verbose: bool = False) -> None:
        """
        Initializes the Jira client.

        Args:
            jira: JIRA instance. If not specified, it will be created through
                JiraAuthenticator.
            verbose: Flag for verbose logging mode.
        """
        # Logger initialization
        self.logger = get_logger()
        self.logger.set_verbose(verbose)

        if jira is None:
            authenticator = JiraAuthenticator()
            self.jira = authenticator.authenticate()
        else:
            self.jira = jira

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a single issue in Jira.

        Args:
            issue_data: Dictionary with data for creating an issue. Must contain
                required fields for project, issue type, and summary, and may
                also contain additional fields such as description, priority,
                assignee, etc.

        Returns:
            dict: Result of the issue creation operation.

            On success contains:
                success (bool): True if the issue was successfully created.
                issue_key (str): Key of the created issue.

            On error contains:
                success (bool): False if an error occurred during issue creation.
                error (str): Error message.
        """
        try:
            issue = self.jira.create_issue(fields=issue_data)
            self.logger.debug(f"Created issue with key: {issue.key}")
            return {"success": True, "issue_key": issue.key}
        except JIRAError as e:
            self.logger.debug(f"Error creating issue: {str(e)}")
            return {"success": False, "error": str(e)}

    def link_to_epic(self, issue_key: str, epic_key: str) -> Dict[str, Any]:
        """
        Link an issue to an epic.

        Args:
            issue_key: Key of the issue to be linked to the epic.
            epic_key: Key of the epic to which the issue should be linked.

        Returns:
            dict: Result of the operation to link the issue to the epic.

            On success contains:
                success (bool): True if the issue was successfully linked to the epic.

            On error contains:
                success (bool): False if an error occurred while linking
                    the issue to the epic.
                error (str): Error message.
        """
        try:
            self.jira.add_issues_to_epic(epic_key, [issue_key])
            self.logger.debug(f"Issue {issue_key} linked to epic {epic_key}")
            return {"success": True}
        except JIRAError as e:
            self.logger.debug(f"Error linking to epic {epic_key}: {str(e)}")
            return {"success": False, "error": str(e)}

    def create_issue_link(
        self, link_type: str, inward_issue: str, outward_issue: str
    ) -> Dict[str, Any]:
        """
        Create a link between two issues.

        Args:
            link_type: Type of link between issues.
            inward_issue: Key of the issue that will be linked as inward.
            outward_issue: Key of the issue that will be linked as outward.

        Returns:
            dict: Result of the operation to create a link between issues.

            On success contains:
                success (bool): True if the link was successfully created.

            On error contains:
                success (bool): False if an error occurred while creating the link.
                error (str): Error message.
        """
        try:
            self.jira.create_issue_link(
                type=link_type, inwardIssue=inward_issue, outwardIssue=outward_issue
            )
            self.logger.debug(
                f"Created link between issues {inward_issue} and {outward_issue} "
                f"of type '{link_type}'"
            )
            return {"success": True}
        except JIRAError as e:
            self.logger.debug(f"Error creating link between issues: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_issue_link_types(self) -> List[str]:
        """
        Get a list of available issue link types.

        Returns:
            List[str]: List of available issue link types.
        """
        try:
            link_types = self.jira.issue_link_types()
            # Extract the names of the link types
            link_type_names = [link_type.name for link_type in link_types]
            self.logger.debug(f"Retrieved link types: {link_type_names}")
            return link_type_names
        except JIRAError as e:
            self.logger.debug(f"Error retrieving link types: {str(e)}")
            return []
