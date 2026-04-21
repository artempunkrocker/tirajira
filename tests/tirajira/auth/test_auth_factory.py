from unittest.mock import patch

import pytest

from tirajira.auth.auth_factory import AuthFactory
from tirajira.auth.auth_strategy import BasicAuthStrategy, PatAuthStrategy


def test_auth_factory_create_pat_strategy():
    """Тест: фабрика создает PAT стратегию когда есть JIRA_PAT_TOKEN"""
    with patch.dict(
        "os.environ",
        {
            "JIRA_SERVER": "https://test.atlassian.net",
            "JIRA_PAT_TOKEN": "pat_token_123",
        },
    ):
        strategy = AuthFactory.create_auth_strategy()
        assert isinstance(strategy, PatAuthStrategy)
        assert strategy.server == "https://test.atlassian.net"
        assert strategy.pat_token == "pat_token_123"


def test_auth_factory_create_basic_auth_strategy():
    """Тест: фабрика создает базовую стратегию когда нет JIRA_PAT_TOKEN"""
    with patch.dict(
        "os.environ",
        {
            "JIRA_SERVER": "https://test.atlassian.net",
            "JIRA_EMAIL": "test@example.com",
            "JIRA_API_TOKEN": "token123",
        },
        clear=True,
    ):
        strategy = AuthFactory.create_auth_strategy()
        assert isinstance(strategy, BasicAuthStrategy)
        assert strategy.server == "https://test.atlassian.net"
        assert strategy.email == "test@example.com"
        assert strategy.api_token == "token123"


def test_auth_factory_pat_missing_server():
    """Тест: фабрика выбрасывает исключение при отсутствии JIRA_SERVER для PAT"""
    with patch.dict(
        "os.environ",
        {
            "JIRA_PAT_TOKEN": "pat_token_123",
        },
        clear=True,
    ):
        with pytest.raises(
            ValueError, match="JIRA_SERVER is required for PAT authentication"
        ):
            AuthFactory.create_auth_strategy()


def test_auth_factory_basic_auth_missing_server():
    """Тест: фабрика выбрасывает исключение при отсутствии JIRA_SERVER
    для базовой аутентификации"""
    with patch.dict(
        "os.environ",
        {
            "JIRA_EMAIL": "test@example.com",
            "JIRA_API_TOKEN": "token123",
        },
        clear=True,
    ):
        with pytest.raises(
            ValueError, match="JIRA_SERVER is required for basic authentication"
        ):
            AuthFactory.create_auth_strategy()


def test_auth_factory_basic_auth_missing_email():
    """Тест: фабрика выбрасывает исключение при отсутствии JIRA_EMAIL
    для базовой аутентификации"""
    with patch.dict(
        "os.environ",
        {
            "JIRA_SERVER": "https://test.atlassian.net",
            "JIRA_API_TOKEN": "token123",
        },
        clear=True,
    ):
        with pytest.raises(
            ValueError, match="JIRA_EMAIL is required for basic authentication"
        ):
            AuthFactory.create_auth_strategy()


def test_auth_factory_basic_auth_missing_api_token():
    """Тест: фабрика выбрасывает исключение при отсутствии JIRA_API_TOKEN
    для базовой аутентификации"""
    with patch.dict(
        "os.environ",
        {
            "JIRA_SERVER": "https://test.atlassian.net",
            "JIRA_EMAIL": "test@example.com",
        },
        clear=True,
    ):
        with pytest.raises(
            ValueError, match="JIRA_API_TOKEN is required for basic authentication"
        ):
            AuthFactory.create_auth_strategy()
