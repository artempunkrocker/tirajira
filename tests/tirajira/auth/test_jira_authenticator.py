from unittest.mock import Mock, patch

import pytest

from tirajira.auth.jira_authenticator import JiraAuthenticator


def test_jira_authenticator_with_strategy():
    """Тест: аутентификатор использует переданную стратегию"""
    # Создаем мок стратегии
    mock_strategy = Mock()
    mock_jira_client = Mock()
    mock_strategy.authenticate.return_value = mock_jira_client
    mock_strategy.get_auth_params.return_value = {
        "server": "https://test.atlassian.net",
        "auth_type": "basic_auth",
    }

    # Создаем аутентификатор с мок стратегией
    authenticator = JiraAuthenticator(mock_strategy)

    # Проверяем аутентификацию
    jira_client = authenticator.authenticate()
    assert jira_client is not None
    assert jira_client == mock_jira_client
    mock_strategy.authenticate.assert_called_once()
    mock_strategy.get_auth_params.assert_called_once()


@patch("tirajira.auth.jira_authenticator.AuthFactory")
def test_jira_authenticator_without_strategy(mock_auth_factory):
    """Тест: аутентификатор создает стратегию через фабрику если она не передана"""
    # Создаем мок стратегии и фабрики
    mock_strategy = Mock()
    mock_jira_client = Mock()
    mock_strategy.authenticate.return_value = mock_jira_client
    mock_strategy.get_auth_params.return_value = {
        "server": "https://test.atlassian.net",
        "auth_type": "basic_auth",
    }
    mock_auth_factory.create_auth_strategy.return_value = mock_strategy

    # Создаем аутентификатор без стратегии
    authenticator = JiraAuthenticator()

    # Проверяем аутентификацию
    jira_client = authenticator.authenticate()
    assert jira_client is not None
    assert jira_client == mock_jira_client
    mock_auth_factory.create_auth_strategy.assert_called_once()
    mock_strategy.authenticate.assert_called_once()
    mock_strategy.get_auth_params.assert_called_once()


@patch("tirajira.auth.jira_authenticator.AuthFactory")
def test_jira_authenticator_authentication_failure(mock_auth_factory):
    """Тест: аутентификатор обрабатывает ошибки аутентификации"""
    # Создаем мок стратегии которая выбрасывает исключение
    mock_strategy = Mock()
    mock_strategy.authenticate.side_effect = Exception("Authentication failed")
    mock_strategy.get_auth_params.return_value = {
        "server": "https://test.atlassian.net",
        "auth_type": "basic_auth",
    }
    mock_auth_factory.create_auth_strategy.return_value = mock_strategy

    # Создаем аутентификатор
    authenticator = JiraAuthenticator()

    # Проверяем что исключение пробрасывается
    with pytest.raises(Exception, match="Authentication failed"):
        authenticator.authenticate()

    mock_auth_factory.create_auth_strategy.assert_called_once()
    mock_strategy.authenticate.assert_called_once()
    mock_strategy.get_auth_params.assert_called_once()
