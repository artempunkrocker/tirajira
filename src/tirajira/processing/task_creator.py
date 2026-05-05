"""
Module for creating Jira issues from files.
"""

import os
from typing import Any, Dict, List, Optional

from ..core.issue_link import IssueLink
from ..core.rate_limiter import RateLimiter
from ..file_loaders import create_file_loader
from ..integrations.jira_client import JiraClient
from ..logger import get_logger
from ..utils.path_validation import validate_file_path
from .report_generator import ReportGenerator


class TaskCreator:
    """Class for creating Jira issues from files."""

    def __init__(
        self,
        jira_client: Optional[JiraClient] = None,
        rate_limiter: Optional[RateLimiter] = None,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the task creator.

        Args:
            jira_client: Jira client. If not specified, a new one will be created.
            rate_limiter: Request rate limiter. If not specified, a new one
                will be created.
            verbose: Verbose logging mode flag.
        """
        self.logger = get_logger()
        self.logger.set_verbose(verbose)

        self._jira_client = jira_client
        self._rate_limiter = rate_limiter
        self._verbose = verbose

        self._jira_client_instance: Optional[JiraClient] = None
        self._rate_limiter_instance: Optional[RateLimiter] = None
        self._report_generator = ReportGenerator()

    def _transform_linking_to_issue_links(self, issues: List[Dict[Any, Any]]) -> None:
        """Transform linking information from file format to IssueLink objects."""
        for issue in issues:
            if not isinstance(issue, dict):
                continue

            linking_data = issue.get("linking")
            if linking_data is None:
                continue

            issue_links = self._extract_issue_links(linking_data)

            # Add transformed links to issue and remove original field
            if issue_links:
                issue["issue_links"] = issue_links
            if "linking" in issue:
                del issue["linking"]

    def _extract_issue_links(self, linking_data: Any) -> List[IssueLink]:
        """Extract IssueLink objects from linking data."""
        issue_links = []

        # Handle both single object and list of objects
        if isinstance(linking_data, dict):
            target_key = linking_data.get("target_key")
            link_type = linking_data.get("link_type")
            if target_key and link_type:
                issue_links.append(
                    IssueLink(target_key=target_key, link_type=link_type)
                )
        elif isinstance(linking_data, list):
            for link_item in linking_data:
                if isinstance(link_item, dict):
                    target_key = link_item.get("target_key")
                    link_type = link_item.get("link_type")
                    if target_key and link_type:
                        issue_links.append(
                            IssueLink(target_key=target_key, link_type=link_type)
                        )

        return issue_links

    @property
    def jira_client(self) -> JiraClient:
        if self._jira_client_instance is None:
            if self._jira_client is not None:
                self._jira_client_instance = self._jira_client
            else:
                self._jira_client_instance = JiraClient(verbose=self._verbose)
        return self._jira_client_instance

    @property
    def rate_limiter(self) -> RateLimiter:
        if self._rate_limiter_instance is None:
            if self._rate_limiter is not None:
                self._rate_limiter_instance = self._rate_limiter
            else:
                self._rate_limiter_instance = RateLimiter(
                    self.jira_client, verbose=self._verbose
                )
        return self._rate_limiter_instance

    def create_from_file(
        self,
        file_path: str,
        max_concurrent_requests: int = 10,
        min_request_interval: float = 1.0,
        stop_on_error: bool = False,
        verbose: bool = False,
        report_file: Optional[str] = None,
    ) -> int:
        """
        Create issues based on a list from a file.

        Args:
            file_path: Path to the file with issues.
            max_concurrent_requests: Maximum number of concurrent requests.
            min_request_interval: Minimum interval between requests in seconds.
            stop_on_error: Stop processing when an error occurs.
            verbose: Verbose logging mode flag.
            report_file: Path to the report file (None - don't save report,
                        True - automatically generate filename,
                        str - use the specified filename).

        Returns:
            Number of successfully created issues.
        """
        self.logger.set_verbose(verbose)

        if hasattr(self.rate_limiter, "logger"):
            self.rate_limiter.logger.set_verbose(verbose)

        self.logger.info(f"Starting issue creation from file: {file_path}")

        try:
            validate_file_path(file_path)
            _, file_extension = os.path.splitext(file_path)
            loader = create_file_loader(file_extension)
            issues = loader.load_issues(file_path)
            self.logger.info(f"Loaded {len(issues)} issues from file")

            self._transform_linking_to_issue_links(issues)

            successful_count, processing_details_with_none = self.rate_limiter.process(
                issues,
                max_concurrent_requests=max_concurrent_requests,
                min_request_interval=min_request_interval,
                stop_on_error=stop_on_error,
                verbose=verbose,
            )

            processing_details = [
                detail for detail in processing_details_with_none if detail is not None
            ]

            self.logger.success(
                f"Successfully created {successful_count} out of {len(issues)} issues"
            )

            if report_file is not None:
                self._report_generator.generate_report(
                    source_file=file_path,
                    processing_details=processing_details,
                    report_file=report_file,
                    successful_count=successful_count,
                    total_count=len(issues),
                )

            return successful_count

        except Exception as e:
            self.logger.error(f"Error creating issues: {e}")
            from ..exceptions import TaskCreatorError

            raise TaskCreatorError(f"Error creating issues: {e}") from e

    def _save_report(
        self,
        source_file: str,
        processing_details: list,
        report_file: str,
        successful_count: int,
        total_count: int,
    ) -> None:
        """
        Saves a report on operation execution.

        Args:
            source_file: Path to the source file with issues.
            processing_details: Details of issue processing.
            report_file: Path to the report file.
            successful_count: Number of successfully created issues.
            total_count: Total number of issues.
        """
        try:
            jira_server = os.getenv("JIRA_SERVER")

            self._report_generator.generate_report(
                source_file=source_file,
                processing_details=processing_details,
                report_file=report_file,
                successful_count=successful_count,
                total_count=total_count,
                jira_server=jira_server,
            )
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
