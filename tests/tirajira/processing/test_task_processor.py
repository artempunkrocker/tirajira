"""
Tests for the TaskProcessor component.
"""

from unittest.mock import Mock, patch

import pytest

from tirajira.core.issue_link import IssueLink
from tirajira.processing.task_processor import TaskProcessor


class TestTaskProcessor:
    """Tests for the TaskProcessor class."""

    @patch("tirajira.processing.task_processor.get_logger")
    def test_init(self, mock_get_logger):
        """Test: TaskProcessor initialization."""
        # Mock the logger so it doesn't output to console
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Create mock for JiraClientInterface
        mock_jira_client = Mock()

        # Create an instance of TaskProcessor
        processor = TaskProcessor(mock_jira_client)

        # Check that jira_client is set correctly
        assert processor.jira_client == mock_jira_client

        # Check that logger is created
        assert processor.logger == mock_logger

    @pytest.mark.parametrize(
        "success,epic_key,expected_calls",
        [
            (True, None, 1),  # Successful creation without epic
            (True, "PROJ-100", 2),  # Successful creation with epic
            (False, None, 1),  # Error creating without epic
            (False, "PROJ-100", 1),  # Error creating with epic (epic is not linked)
        ],
    )
    @patch("tirajira.processing.task_processor.get_logger")
    def test_process_single_issue(
        self, mock_get_logger, success, epic_key, expected_calls
    ):
        """Test: processing a single issue."""
        # Mock the logger so it doesn't output to console
        mock_logger = Mock()
        mock_logger.success = Mock()
        mock_logger.error = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_get_logger.return_value = mock_logger

        # Create mocks
        mock_jira_client = Mock()
        mock_rate_controller = Mock()

        # Set up return values
        if success:
            mock_jira_client.create_issue.return_value = {
                "success": True,
                "issue_key": "PROJ-123",
            }
            mock_jira_client.link_to_epic.return_value = {"success": True}
            mock_jira_client.create_issue_link.return_value = {"success": True}
        else:
            mock_jira_client.create_issue.return_value = {
                "success": False,
                "error": "Create failed",
            }

        # Create an instance of TaskProcessor
        processor = TaskProcessor(mock_jira_client)

        # Prepare issue data
        issue_data = {"summary": "Test task", "project": {"key": "PROJ"}}
        if epic_key:
            issue_data["epic_key"] = epic_key

        # Call the method under test
        task_detail, result_success = processor.process_single_issue(
            issue_data, 0, mock_rate_controller
        )

        # Check wait_if_needed calls
        assert mock_rate_controller.wait_if_needed.call_count == expected_calls

        # Check create_issue calls
        mock_jira_client.create_issue.assert_called_once()

        # Check results
        assert result_success == success

        if success:
            assert task_detail["status"] == "success"
            assert task_detail["issue_key"] == "PROJ-123"
            # Check link_to_epic call if epic_key is specified
            if epic_key:
                mock_jira_client.link_to_epic.assert_called_once_with(
                    "PROJ-123", epic_key
                )
            else:
                mock_jira_client.link_to_epic.assert_not_called()
        else:
            assert task_detail["status"] == "failure"
            assert "error_message" in task_detail
            # link_to_epic should not be called when creation fails
            mock_jira_client.link_to_epic.assert_not_called()

    @pytest.mark.parametrize(
        "link_success,expected_calls",
        [
            (True, 3),  # 1 for issue creation + 2 for links
            (False, 3),  # 1 for issue creation + 2 for links (even with error)
        ],
    )
    @patch("tirajira.processing.task_processor.get_logger")
    def test_process_single_issue_with_issue_links(
        self, mock_get_logger, link_success, expected_calls
    ):
        """Test: processing a single issue with links."""
        # Mock the logger so it doesn't output to console
        mock_logger = Mock()
        mock_logger.success = Mock()
        mock_logger.error = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_get_logger.return_value = mock_logger

        # Create mocks
        mock_jira_client = Mock()
        mock_rate_controller = Mock()

        # Set up return values
        mock_jira_client.create_issue.return_value = {
            "success": True,
            "issue_key": "PROJ-123",
        }
        mock_jira_client.link_to_epic.return_value = {"success": True}
        mock_jira_client.create_issue_link.return_value = {
            "success": link_success,
            "error": "Link failed" if not link_success else None,
        }

        # Create an instance of TaskProcessor
        processor = TaskProcessor(mock_jira_client)

        # Prepare issue data with links
        issue_links = [
            IssueLink(target_key="PROJ-100", link_type="relates to"),
            IssueLink(target_key="PROJ-101", link_type="blocks"),
        ]
        issue_data = {
            "summary": "Test task",
            "project": {"key": "PROJ"},
            "issue_links": issue_links,
        }

        # Call the method under test
        task_detail, result_success = processor.process_single_issue(
            issue_data, 0, mock_rate_controller
        )

        # Check wait_if_needed calls (1 for creation + 2 for links)
        assert mock_rate_controller.wait_if_needed.call_count == expected_calls

        # Check create_issue calls
        mock_jira_client.create_issue.assert_called_once()

        # Check create_issue calls_link
        assert mock_jira_client.create_issue_link.call_count == 2

        # Check the first create_issue_link call
        mock_jira_client.create_issue_link.assert_any_call(
            link_type="relates to", inward_issue="PROJ-123", outward_issue="PROJ-100"
        )

        # Check the second create_issue_link call
        mock_jira_client.create_issue_link.assert_any_call(
            link_type="blocks", inward_issue="PROJ-123", outward_issue="PROJ-101"
        )

        # Check results
        assert result_success
        assert task_detail["status"] == "success"
        assert task_detail["issue_key"] == "PROJ-123"

        # Check link information
        assert "links" in task_detail
        assert "successful" in task_detail["links"]
        assert "failed" in task_detail["links"]

        if link_success:
            assert len(task_detail["links"]["successful"]) == 2
            assert len(task_detail["links"]["failed"]) == 0

            successful_links = task_detail["links"]["successful"]
            expected_link_1 = {"target_key": "PROJ-100", "link_type": "relates to"}
            expected_link_2 = {"target_key": "PROJ-101", "link_type": "blocks"}
            assert expected_link_1 in successful_links
            assert expected_link_2 in successful_links
        else:
            assert len(task_detail["links"]["successful"]) == 0
            assert len(task_detail["links"]["failed"]) == 2

            failed_links = task_detail["links"]["failed"]
            assert len(failed_links) == 2
            for link in failed_links:
                assert "target_key" in link
                assert "link_type" in link
                assert "error" in link
                assert link["error"] == "Link failed"

        # Check logging
        mock_logger.success.assert_called_once_with("Issue created: PROJ-123")
        # We expect:
        # 2 info calls for successful link creations (if link_success is True)
        # 0 info calls for failed link creations (if link_success is False)
        expected_info_calls = 2 if link_success else 0
        assert mock_logger.info.call_count == expected_info_calls
        assert mock_logger.error.call_count == (2 if not link_success else 0)

    @patch("tirajira.processing.task_processor.get_logger")
    def test_process_single_issue_with_invalid_issue_links(self, mock_get_logger):
        """Test: processing a single issue with invalid links."""
        # Mock the logger so it doesn't output to console
        mock_logger = Mock()
        mock_logger.success = Mock()
        mock_logger.error = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_get_logger.return_value = mock_logger

        # Create mocks
        mock_jira_client = Mock()
        mock_rate_controller = Mock()

        # Set up return values
        mock_jira_client.create_issue.return_value = {
            "success": True,
            "issue_key": "PROJ-123",
        }
        mock_jira_client.link_to_epic.return_value = {"success": True}
        mock_jira_client.create_issue_link.return_value = {"success": True}

        # Create an instance of TaskProcessor
        processor = TaskProcessor(mock_jira_client)

        # Prepare issue data with invalid links
        issue_links = [
            IssueLink(target_key=None, link_type="relates to"),  # No target_key
            IssueLink(target_key="PROJ-101", link_type=None),  # No link_type
            "invalid_link",  # Not an IssueLink object
            IssueLink(target_key="PROJ-102", link_type="blocks"),  # Valid link
        ]
        issue_data = {
            "summary": "Test task",
            "project": {"key": "PROJ"},
            "issue_links": issue_links,
        }

        # Call the method under test
        task_detail, result_success = processor.process_single_issue(
            issue_data, 0, mock_rate_controller
        )

        # Check create_issue calls
        mock_jira_client.create_issue.assert_called_once()

        # Check that only one valid link was processed
        mock_jira_client.create_issue_link.assert_called_once_with(
            link_type="blocks", inward_issue="PROJ-123", outward_issue="PROJ-102"
        )

        # Check results
        assert result_success
        assert task_detail["status"] == "success"
        assert task_detail["issue_key"] == "PROJ-123"

        # Check link information
        assert "links" in task_detail
        assert "successful" in task_detail["links"]
        assert "failed" in task_detail["links"]

        assert len(task_detail["links"]["successful"]) == 1
        assert len(task_detail["links"]["failed"]) == 3

        successful_links = task_detail["links"]["successful"]
        assert {"target_key": "PROJ-102", "link_type": "blocks"} in successful_links

        failed_links = task_detail["links"]["failed"]
        assert len(failed_links) == 3

        failed_link_targets = [link.get("target_key") for link in failed_links]
        failed_link_types = [link.get("link_type") for link in failed_links]

        assert None in failed_link_targets or "Invalid link data" in [
            link.get("error", "") for link in failed_links
        ]

        error_messages = [link.get("error", "") for link in failed_links]
        assert None in failed_link_types or "Invalid link data" in error_messages

        # Check warning logging
        assert mock_logger.warning.call_count == 3  # 3 incorrect links


@pytest.mark.parametrize(
    "exception_type",
    [
        Exception("Generic error"),
        ValueError("Value error"),
        ConnectionError("Connection error"),
    ],
)
@patch("tirajira.processing.task_processor.get_logger")
def test_process_single_issue_rate_limit_wait_exception(
    mock_get_logger, exception_type
):
    """Test: handling exceptions when waiting for rate limiting."""
    # Mock the logger so it doesn't output to console
    mock_logger = Mock()
    mock_logger.success = Mock()
    mock_logger.error = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_get_logger.return_value = mock_logger

    # Create mocks
    mock_jira_client = Mock()
    mock_rate_controller = Mock()

    # Set up wait_if_needed to throw an exception
    mock_rate_controller.wait_if_needed.side_effect = exception_type

    # Set up return value for create_issue
    # (will not be called due to exception)
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }

    # Create an instance of TaskProcessor
    processor = TaskProcessor(mock_jira_client)

    # Prepare issue data
    issue_data = {"summary": "Test task", "project": {"key": "PROJ"}}

    # Call the method under test and expect that an exception will be thrown
    with pytest.raises(type(exception_type)):
        processor.process_single_issue(issue_data, 0, mock_rate_controller)

        # Check that wait_if_needed was called
    mock_rate_controller.wait_if_needed.assert_called_once()

    # Check that create_issue was not called
    mock_jira_client.create_issue.assert_not_called()


@patch("tirajira.processing.task_processor.get_logger")
def test_process_single_issue_create_issue_failure(mock_get_logger):
    """Test: handling errors when creating an issue."""
    # Mock the logger so it doesn't output to console
    mock_logger = Mock()
    mock_logger.success = Mock()
    mock_logger.error = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_get_logger.return_value = mock_logger

    # Create mocks
    mock_jira_client = Mock()
    mock_rate_controller = Mock()

    # Set up create_issue to return an error
    mock_jira_client.create_issue.return_value = {
        "success": False,
        "error": "Create issue failed",
    }

    # Create an instance of TaskProcessor
    processor = TaskProcessor(mock_jira_client)

    # Prepare issue data
    issue_data = {"summary": "Test task", "project": {"key": "PROJ"}}

    # Call the method under test
    task_detail, result_success = processor.process_single_issue(
        issue_data, 0, mock_rate_controller
    )

    # Check that wait_if_needed was called
    mock_rate_controller.wait_if_needed.assert_called_once()

    # Check that create_issue was called
    mock_jira_client.create_issue.assert_called_once()

    # Check results - should be unsuccessful
    assert not result_success
    assert task_detail["status"] == "failure"
    assert "error_message" in task_detail
    assert "Create issue failed" in task_detail["error_message"]

    # Check error logging
    mock_logger.error.assert_called_once()


@patch("tirajira.processing.task_processor.get_logger")
def test_process_single_issue_link_to_epic_failure(mock_get_logger):
    """Test: handling errors when linking to epic."""
    # Mock the logger so it doesn't output to console
    mock_logger = Mock()
    mock_logger.success = Mock()
    mock_logger.error = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_get_logger.return_value = mock_logger

    # Create mocks
    mock_jira_client = Mock()
    mock_rate_controller = Mock()

    # Set up return values
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }

    # Set up link_to_epic to return an error
    mock_jira_client.link_to_epic.return_value = {
        "success": False,
        "error": "Link to epic failed",
    }

    # Create an instance of TaskProcessor
    processor = TaskProcessor(mock_jira_client)

    # Prepare issue data with epic
    issue_data = {
        "summary": "Test task",
        "project": {"key": "PROJ"},
        "epic_key": "PROJ-100",
    }

    # Call the method under test
    task_detail, result_success = processor.process_single_issue(
        issue_data, 0, mock_rate_controller
    )

    # Check that wait_if_needed was called twice
    # (once for creation, once for epic)
    assert mock_rate_controller.wait_if_needed.call_count == 2

    # Check that create_issue was called
    mock_jira_client.create_issue.assert_called_once()

    # Check that link_to_epic was called
    mock_jira_client.link_to_epic.assert_called_once_with("PROJ-123", "PROJ-100")

    # Check results - issue creation successful, but with linking error
    assert result_success
    assert task_detail["status"] == "success"
    assert task_detail["issue_key"] == "PROJ-123"
    assert "error_message" in task_detail
    assert "Link to epic failed" in task_detail["error_message"]

    # Check logging
    mock_logger.success.assert_called_once_with("Issue created: PROJ-123")
    mock_logger.error.assert_called_once()


@patch("tirajira.processing.task_processor.get_logger")
def test_process_single_issue_create_issue_link_failure(mock_get_logger):
    """Test: handling errors when creating links between issues."""
    # Mock the logger so it doesn't output to console
    mock_logger = Mock()
    mock_logger.success = Mock()
    mock_logger.error = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_get_logger.return_value = mock_logger

    # Create mocks
    mock_jira_client = Mock()
    mock_rate_controller = Mock()

    # Set up return values
    mock_jira_client.create_issue.return_value = {
        "success": True,
        "issue_key": "PROJ-123",
    }

    # Set up create_issue_link to return an error
    mock_jira_client.create_issue_link.return_value = {
        "success": False,
        "error": "Create link failed",
    }

    # Create an instance of TaskProcessor
    processor = TaskProcessor(mock_jira_client)

    # Prepare issue data with links
    issue_links = [IssueLink(target_key="PROJ-100", link_type="relates to")]
    issue_data = {
        "summary": "Test task",
        "project": {"key": "PROJ"},
        "issue_links": issue_links,
    }

    # Call the method under test
    task_detail, result_success = processor.process_single_issue(
        issue_data, 0, mock_rate_controller
    )

    # Check that wait_if_needed was called twice
    # (once for creation, once for link)
    assert mock_rate_controller.wait_if_needed.call_count == 2

    # Check that create_issue was called
    mock_jira_client.create_issue.assert_called_once()

    # Check that create_issue_link was called
    mock_jira_client.create_issue_link.assert_called_once_with(
        link_type="relates to", inward_issue="PROJ-123", outward_issue="PROJ-100"
    )

    # Check results - issue creation successful, but with link error
    assert result_success
    assert task_detail["status"] == "success"
    assert task_detail["issue_key"] == "PROJ-123"
    assert "error_message" in task_detail
    assert "Create link failed" in task_detail["error_message"]
    assert "links" in task_detail
    assert "failed" in task_detail["links"]
    assert len(task_detail["links"]["failed"]) == 1

    # Check logging
    mock_logger.success.assert_called_once_with("Issue created: PROJ-123")
    mock_logger.error.assert_called_once()


if __name__ == "__main__":
    pytest.main()
