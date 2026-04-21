"""
Модуль для аутентификации в Jira API.
"""

import logging
from typing import Optional

from jira import JIRA

from .auth_factory import AuthFactory
from .auth_strategy import AuthStrategy

logger = logging.getLogger(__name__)


class JiraAuthenticator:
    """Аутентификатор для Jira API."""

    def __init__(self, auth_strategy: Optional[AuthStrategy] = None):
        """
        Инициализирует аутентификатор.

        Args:
            auth_strategy: Стратегия аутентификации. Если не указана, будет
                           создана через фабрику.
        """
        self.auth_strategy = auth_strategy or AuthFactory.create_auth_strategy()

    def authenticate(self) -> JIRA:
        """
        Аутентифицирует и возвращает клиент JIRA.

        Returns:
            JIRA: Аутентифицированный клиент JIRA

        Raises:
            Exception: Если аутентификация не удалась
        """
        try:
            auth_params = self.auth_strategy.get_auth_params()
            logger.info(f"Аутентификация в Jira: {auth_params}")
            jira_client = self.auth_strategy.authenticate()
            logger.info("Успешная аутентификация в Jira")
            return jira_client
        except Exception as e:
            logger.error(f"Ошибка аутентификации в Jira: {e}")
            raise
