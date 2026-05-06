"""
Module for processing Jira issues (creating issues, linking to epics,
and creating links).
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple

from ..core.issue_link import IssueLink
from ..integrations.jira_client_interface import JiraClientInterface
from ..logger import get_logger


class TaskProcessor:
    """Component for processing Jira issues."""

    def __init__(self, jira_client: JiraClientInterface) -> None:
        """
        Initializes the task processor.

        Args:
            jira_client: Client for interacting with the Jira API.
        """
        self.jira_client = jira_client
        self.logger = get_logger()

    def process_single_issue(
        self,
        issue_data: Dict[Any, Any],
        issue_index: int,
        rate_controller: Any,  # RateLimitController instance
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Processes a single issue taking into account request rate limitations.

        Args:
            issue_data: Issue data for creation.
            issue_index: Index of the issue in the list.
            rate_controller: Request rate limit controller.

        Returns:
            A tuple of a dictionary with issue processing details and a boolean value
            indicating the success of the operation.
        """
        rate_controller.wait_if_needed()

        original_issue_data = issue_data.copy() if isinstance(issue_data, dict) else {}

        # Extract epic_key if it exists, so we don't pass it to the Jira API
        epic_key = (
            issue_data.pop("epic_key", None) if isinstance(issue_data, dict) else None
        )

        # Extract issue_links if they exist
        issue_links = (
            issue_data.pop("issue_links", []) if isinstance(issue_data, dict) else []
        )

        processed_at = datetime.now().isoformat()

        result = self.jira_client.create_issue(issue_data)
        task_detail = {
            "status": "success" if result["success"] else "failure",
            "issue_data": original_issue_data,
            "processed_at": processed_at,
            "id": issue_index,
        }

        success = result["success"]

        if success:
            self.logger.success(f"Issue created: {result['issue_key']}")
            task_detail["issue_key"] = result["issue_key"]

            # Link to epic if specified (also requires waiting)
            if epic_key:
                rate_controller.wait_if_needed()  # Wait before the next request
                link_result = self.jira_client.link_to_epic(
                    result["issue_key"], epic_key
                )
                if link_result["success"]:
                    self.logger.info(
                        f"Issue {result['issue_key']} linked to epic {epic_key}"
                    )
                else:
                    self.logger.error(f"Error linking to epic: {link_result['error']}")
                    # Add error information to issue details
                    task_detail["error_message"] = (
                        f"Epic linking error: {link_result['error']}"
                    )

            # Creating links with other issues if specified
            if issue_links:
                self._process_issue_links(
                    result["issue_key"], issue_links, rate_controller, task_detail
                )
        else:
            self.logger.error(f"Error creating issue: {result['error']}")
            task_detail["error_message"] = result["error"]

        return task_detail, success

    def _process_issue_links(
        self,
        issue_key: str,
        issue_links: List[IssueLink],
        rate_controller: Any,  # RateLimitController instance
        task_detail: Dict[str, Any],
    ) -> None:
        """
        Processes a list of links for the created issue.

        Args:
            issue_key: Key of the created issue.
            issue_links: List of IssueLink objects for creating links.
            rate_controller: Request rate limit controller.
            task_detail: Dictionary with issue processing details.
        """
        task_detail["links"] = {"successful": [], "failed": []}

        for i, link in enumerate(issue_links):
            # Check that link is an IssueLink object
            # and has the required attributes
            if (
                not isinstance(link, IssueLink)
                or not link.target_key
                or not link.link_type
            ):
                self.logger.warning(
                    f"Incorrect link #{i + 1} for issue {issue_key}: "
                    f"required data is missing"
                )
                task_detail["links"]["failed"].append(
                    {
                        "target_key": getattr(link, "target_key", None),
                        "link_type": getattr(link, "link_type", None),
                        "error": "Incorrect link data",
                    }
                )
                continue

            rate_controller.wait_if_needed()

            # In Jira API inward_issue - the issue that receives the link
            # (in this case our issue)
            # outward_issue - the issue that is being linked to (target issue)
            link_result = self.jira_client.create_issue_link(
                link_type=link.link_type,
                inward_issue=issue_key,
                outward_issue=link.target_key,
            )

            if link_result["success"]:
                self.logger.info(
                    f"Created link '{link.link_type}' between issues {issue_key} "
                    f"and {link.target_key}"
                )
                task_detail["links"]["successful"].append(
                    {"target_key": link.target_key, "link_type": link.link_type}
                )
            else:
                error_msg = (
                    f"Error creating link '{link.link_type}' with issue "
                    f"{link.target_key}: {link_result['error']}"
                )
                self.logger.error(error_msg)
                # Add error information to issue details,
                # but continue processing
                if "error_message" not in task_detail:
                    task_detail["error_message"] = error_msg
                else:
                    task_detail["error_message"] += f"; {error_msg}"

                task_detail["links"]["failed"].append(
                    {
                        "target_key": link.target_key,
                        "link_type": link.link_type,
                        "error": link_result["error"],
                    }
                )
