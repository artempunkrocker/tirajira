from unittest.mock import Mock, patch

import pytest
from jira import JIRA
from jira.exceptions import JIRAError

from tirajira.integrations.jira_client import JiraClient


def test_jira_client_init_with_jira_instance():
    """Test: JiraClient initialization with a passed JIRA instance"""
    mock_jira = Mock(spec=JIRA)
    client = JiraClient(jira=mock_jira)
    assert client.jira == mock_jira


def test_jira_client_init_without_jira_instance():
    """Test: JiraClient initialization without a passed JIRA instance"""
    mock_jira = Mock(spec=JIRA)

    with patch(
        "tirajira.integrations.jira_client.JiraAuthenticator"
    ) as mock_auth_class:
        mock_authenticator = Mock()
        mock_authenticator.authenticate.return_value = mock_jira
        mock_auth_class.return_value = mock_authenticator

        client = JiraClient()

        assert client.jira == mock_jira
        mock_auth_class.assert_called_once()
        mock_authenticator.authenticate.assert_called_once()


# Removed tests for environment variables check, as this logic
# is now located in other classes


def test_create_issue_success():
    """Test: successful task creation"""
    mock_jira = Mock(spec=JIRA)
    mock_issue = Mock()
    mock_issue.key = "PROJ-123"
    mock_jira.create_issue.return_value = mock_issue

    client = JiraClient(jira=mock_jira)
    issue_data = {"summary": "Test issue", "project": {"key": "PROJ"}}
    result = client.create_issue(issue_data)

    assert result["success"] is True
    assert result["issue_key"] == "PROJ-123"
    mock_jira.create_issue.assert_called_once_with(fields=issue_data)


def test_create_issue_failure():
    """Test: error when creating a task"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.create_issue.side_effect = JIRAError("Connection error")

    client = JiraClient(jira=mock_jira)
    issue_data = {"summary": "Test issue", "project": {"key": "PROJ"}}
    result = client.create_issue(issue_data)

    assert result["success"] is False
    assert "Connection error" in result["error"]


def test_link_to_epic_success():
    """Test: successful linking of a task to an epic"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.add_issues_to_epic.return_value = None

    client = JiraClient(jira=mock_jira)
    result = client.link_to_epic("PROJ-123", "PROJ-100")

    assert result["success"] is True
    mock_jira.add_issues_to_epic.assert_called_once_with("PROJ-100", ["PROJ-123"])


def test_link_to_epic_failure():
    """Test: error when linking to an epic"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.add_issues_to_epic.side_effect = JIRAError("Link error")

    client = JiraClient(jira=mock_jira)
    result = client.link_to_epic("PROJ-123", "PROJ-100")

    assert result["success"] is False
    assert "Link error" in result["error"]


def test_create_issue_link_success():
    """Test: successful creation of a link between tasks"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.create_issue_link.return_value = None

    client = JiraClient(jira=mock_jira)
    result = client.create_issue_link("Relates", "PROJ-123", "PROJ-124")

    assert result["success"] is True
    mock_jira.create_issue_link.assert_called_once_with(
        type="Relates", inwardIssue="PROJ-123", outwardIssue="PROJ-124"
    )


def test_create_issue_link_failure():
    """Test: error when creating a link between tasks"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.create_issue_link.side_effect = JIRAError("Link creation error")

    client = JiraClient(jira=mock_jira)
    result = client.create_issue_link("Relates", "PROJ-123", "PROJ-124")

    assert result["success"] is False
    assert "Link creation error" in result["error"]


def test_get_issue_link_types_success():
    """Test: successful retrieval of link types between tasks"""
    # Create mock link type objects
    mock_link_type1 = Mock()
    mock_link_type1.name = "Relates"
    mock_link_type2 = Mock()
    mock_link_type2.name = "Blocks"

    mock_jira = Mock(spec=JIRA)
    mock_jira.issue_link_types.return_value = [mock_link_type1, mock_link_type2]

    client = JiraClient(jira=mock_jira)
    result = client.get_issue_link_types()

    assert result == ["Relates", "Blocks"]
    mock_jira.issue_link_types.assert_called_once()


def test_get_issue_link_types_failure():
    """Test: error when retrieving link types between tasks"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.issue_link_types.side_effect = JIRAError("Failed to get link types")

    client = JiraClient(jira=mock_jira)
    result = client.get_issue_link_types()

    assert result == []
    mock_jira.issue_link_types.assert_called_once()


if __name__ == "__main__":
    pytest.main()
