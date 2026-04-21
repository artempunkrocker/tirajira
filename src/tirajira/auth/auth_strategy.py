"""
Модуль стратегий аутентификации для Jira API.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from jira import JIRA


class AuthStrategy(ABC):
    """Абстрактный класс для стратегий аутентификации."""

    @abstractmethod
    def authenticate(self) -> JIRA:
        """Аутентифицирует и возвращает клиент JIRA."""
        pass

    @abstractmethod
    def get_auth_params(self) -> Dict[str, Any]:
        """Возвращает параметры аутентификации для логирования (без секретов)."""
        pass


class BasicAuthStrategy(AuthStrategy):
    """Стратегия базовой аутентификации."""

    def __init__(self, server: str, email: str, api_token: str):
        self.server = server
        self.email = email
        self.api_token = api_token

    def authenticate(self) -> JIRA:
        """Аутентифицирует и возвращает клиент JIRA с базовой аутентификацией."""
        return JIRA(
            server=self.server,
            basic_auth=(self.email, self.api_token),
        )

    def get_auth_params(self) -> Dict[str, Any]:
        """Возвращает параметры аутентификации для логирования."""
        return {"server": self.server, "email": self.email, "auth_type": "basic_auth"}


class PatAuthStrategy(AuthStrategy):
    """Стратегия аутентификации через Personal Access Token."""

    def __init__(self, server: str, pat_token: str):
        self.server = server
        self.pat_token = pat_token

    def authenticate(self) -> JIRA:
        """Аутентифицирует и возвращает клиент JIRA с PAT аутентификацией."""
        return JIRA(
            server=self.server,
            token_auth=self.pat_token,
        )

    def get_auth_params(self) -> Dict[str, Any]:
        """Возвращает параметры аутентификации для логирования."""
        return {"server": self.server, "auth_type": "pat_auth"}
