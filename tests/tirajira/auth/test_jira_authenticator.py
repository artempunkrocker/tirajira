from unittest.mock import Mock, patch

import pytest

from tirajira.auth.jira_authenticator import JiraAuthenticator


def test_jira_authenticator_with_strategy():
    """Test: authenticator uses the provided strategy"""
    # Create mock strategy
    mock_strategy = Mock()
    mock_jira_client = Mock()
    mock_strategy.authenticate.return_value = mock_jira_client
    mock_strategy.get_auth_params.return_value = {
        "server": "https://test.atlassian.net",
        "auth_type": "basic_auth",
    }

    # Create authenticator with mock strategy
    authenticator = JiraAuthenticator(mock_strategy)

    # Check authentication
    jira_client = authenticator.authenticate()
    assert jira_client is not None
    assert jira_client == mock_jira_client
    mock_strategy.authenticate.assert_called_once()
    mock_strategy.get_auth_params.assert_called_once()


@patch("tirajira.auth.jira_authenticator.AuthFactory")
def test_jira_authenticator_without_strategy(mock_auth_factory):
    """Test: authenticator creates strategy via factory if not provided"""
    # Create mock strategy and factory
    mock_strategy = Mock()
    mock_jira_client = Mock()
    mock_strategy.authenticate.return_value = mock_jira_client
    mock_strategy.get_auth_params.return_value = {
        "server": "https://test.atlassian.net",
        "auth_type": "basic_auth",
    }
    mock_auth_factory.create_auth_strategy.return_value = mock_strategy

    # Create authenticator without strategy
    authenticator = JiraAuthenticator()

    # Check authentication
    jira_client = authenticator.authenticate()
    assert jira_client is not None
    assert jira_client == mock_jira_client
    mock_auth_factory.create_auth_strategy.assert_called_once()
    mock_strategy.authenticate.assert_called_once()
    mock_strategy.get_auth_params.assert_called_once()


@patch("tirajira.auth.jira_authenticator.AuthFactory")
def test_jira_authenticator_authentication_failure(mock_auth_factory):
    """Test: authenticator handles authentication errors"""
    # Create mock strategy that throws an exception
    mock_strategy = Mock()
    mock_strategy.authenticate.side_effect = Exception("Authentication failed")
    mock_strategy.get_auth_params.return_value = {
        "server": "https://test.atlassian.net",
        "auth_type": "basic_auth",
    }
    mock_auth_factory.create_auth_strategy.return_value = mock_strategy

    # Create authenticator
    authenticator = JiraAuthenticator()

    # Check that the exception is raised
    with pytest.raises(Exception, match="Authentication failed"):
        authenticator.authenticate()

    mock_auth_factory.create_auth_strategy.assert_called_once()
    mock_strategy.authenticate.assert_called_once()
    mock_strategy.get_auth_params.assert_called_once()
