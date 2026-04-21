"""
Фабрика для создания стратегий аутентификации.
"""

import os

from .auth_strategy import AuthStrategy, BasicAuthStrategy, PatAuthStrategy


class AuthFactory:
    """Фабрика для создания стратегий аутентификации."""

    @staticmethod
    def create_auth_strategy() -> AuthStrategy:
        """
        Создает стратегию аутентификации на основе переменных окружения.

        Returns:
            AuthStrategy: Стратегия аутентификации

        Raises:
            ValueError: Если не удалось создать стратегию из-за отсутствия
                        необходимых переменных окружения
        """
        # Проверяем, какой режим аутентификации использовать
        pat_token = os.getenv("JIRA_PAT_TOKEN")

        if pat_token:
            # Используем токен-аутентификацию (Personal Access Token)
            return AuthFactory._create_pat_strategy(pat_token)
        else:
            # Используем базовую аутентификацию (обратная совместимость)
            return AuthFactory._create_basic_auth_strategy()

    @staticmethod
    def _create_pat_strategy(pat_token: str) -> PatAuthStrategy:
        """Создает стратегию PAT аутентификации."""
        jira_server = os.getenv("JIRA_SERVER")
        if not jira_server:
            raise ValueError("JIRA_SERVER is required for PAT authentication")

        return PatAuthStrategy(jira_server, pat_token)

    @staticmethod
    def _create_basic_auth_strategy() -> BasicAuthStrategy:
        """Создает стратегию базовой аутентификации."""
        jira_server = os.getenv("JIRA_SERVER")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_api_token = os.getenv("JIRA_API_TOKEN")

        if not jira_server:
            raise ValueError("JIRA_SERVER is required for basic authentication")
        if not jira_email:
            raise ValueError("JIRA_EMAIL is required for basic authentication")
        if not jira_api_token:
            raise ValueError("JIRA_API_TOKEN is required for basic authentication")

        return BasicAuthStrategy(jira_server, jira_email, jira_api_token)
