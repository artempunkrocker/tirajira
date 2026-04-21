from unittest.mock import Mock, patch

import pytest
from jira import JIRA

from tirajira.jira_client import JiraClient


def test_jira_client_init_with_jira_instance():
    """Тест: инициализация JiraClient с переданным экземпляром JIRA"""
    mock_jira = Mock(spec=JIRA)
    client = JiraClient(jira=mock_jira)
    assert client.jira == mock_jira


def test_jira_client_init_without_jira_instance():
    """Тест: инициализация JiraClient без переданного экземпляра JIRA"""
    mock_jira = Mock(spec=JIRA)

    with patch("tirajira.jira_client.JiraAuthenticator") as mock_auth_class:
        mock_authenticator = Mock()
        mock_authenticator.authenticate.return_value = mock_jira
        mock_auth_class.return_value = mock_authenticator

        client = JiraClient()

        assert client.jira == mock_jira
        mock_auth_class.assert_called_once()
        mock_authenticator.authenticate.assert_called_once()


# Удалены тесты проверки переменных окружения, так как эта логика
# теперь находится в других классах


def test_create_issue_success():
    """Тест: успешное создание задачи"""
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
    """Тест: ошибка при создании задачи"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.create_issue.side_effect = Exception("Connection error")

    client = JiraClient(jira=mock_jira)
    issue_data = {"summary": "Test issue", "project": {"key": "PROJ"}}
    result = client.create_issue(issue_data)

    assert result["success"] is False
    assert "Connection error" in result["error"]


def test_link_to_epic_success():
    """Тест: успешная привязка задачи к эпику"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.add_issues_to_epic.return_value = None

    client = JiraClient(jira=mock_jira)
    result = client.link_to_epic("PROJ-123", "PROJ-100")

    assert result["success"] is True
    mock_jira.add_issues_to_epic.assert_called_once_with("PROJ-100", ["PROJ-123"])


def test_link_to_epic_failure():
    """Тест: ошибка при привязке к эпику"""
    mock_jira = Mock(spec=JIRA)
    mock_jira.add_issues_to_epic.side_effect = Exception("Link error")

    client = JiraClient(jira=mock_jira)
    result = client.link_to_epic("PROJ-123", "PROJ-100")

    assert result["success"] is False
    assert "Link error" in result["error"]


if __name__ == "__main__":
    pytest.main()
