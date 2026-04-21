from unittest.mock import Mock, patch

from tirajira.auth.auth_strategy import BasicAuthStrategy, PatAuthStrategy


def test_basic_auth_strategy():
    """Тест: стратегия базовой аутентификации"""
    strategy = BasicAuthStrategy(
        "https://test.atlassian.net", "test@example.com", "token123"
    )

    # Проверяем параметры аутентификации
    auth_params = strategy.get_auth_params()
    assert auth_params["server"] == "https://test.atlassian.net"
    assert auth_params["email"] == "test@example.com"
    assert auth_params["auth_type"] == "basic_auth"

    # Проверяем создание клиента JIRA (мокаем JIRA)
    with patch("tirajira.auth.auth_strategy.JIRA") as mock_jira_class:
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance

        jira_client = strategy.authenticate()
        assert jira_client is not None
        mock_jira_class.assert_called_once_with(
            server="https://test.atlassian.net",
            basic_auth=("test@example.com", "token123"),
        )


def test_pat_auth_strategy():
    """Тест: стратегия PAT аутентификации"""
    strategy = PatAuthStrategy("https://test.atlassian.net", "pat_token_123")

    # Проверяем параметры аутентификации
    auth_params = strategy.get_auth_params()
    assert auth_params["server"] == "https://test.atlassian.net"
    assert auth_params["auth_type"] == "pat_auth"

    # Проверяем создание клиента JIRA (мокаем JIRA)
    with patch("tirajira.auth.auth_strategy.JIRA") as mock_jira_class:
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance

        jira_client = strategy.authenticate()
        assert jira_client is not None
        mock_jira_class.assert_called_once_with(
            server="https://test.atlassian.net",
            token_auth="pat_token_123",
        )
