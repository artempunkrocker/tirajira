"""
Модуль для работы с Jira API.
"""

from typing import Optional

from jira import JIRA

from .auth.jira_authenticator import JiraAuthenticator
from .logger import get_logger


class JiraClient:
    """Клиент для взаимодействия с Jira API."""

    def __init__(self, jira: Optional[JIRA] = None, verbose: bool = False) -> None:
        """
        Инициализирует клиент Jira.

        Args:
            jira: Экземпляр JIRA. Если не указан, будет создан через JiraAuthenticator.
            verbose: Флаг подробного режима логирования.
        """
        # Инициализация логгера
        self.logger = get_logger()
        self.logger.set_verbose(verbose)

        if jira is None:
            authenticator = JiraAuthenticator()
            self.jira = authenticator.authenticate()
        else:
            self.jira = jira

    def create_issue(self, issue_data: dict) -> dict:
        """Создание одной задачи в Jira."""
        # Используем логгер из экземпляра класса
        logger = self.logger

        try:
            issue = self.jira.create_issue(fields=issue_data)
            logger.debug(f"Создана задача с ключом: {issue.key}")
            return {"success": True, "issue_key": issue.key}
        except Exception as e:
            logger.debug(f"Ошибка создания задачи: {str(e)}")
            return {"success": False, "error": str(e)}

    def link_to_epic(self, issue_key: str, epic_key: str) -> dict:
        """Привязка задачи к эпику."""
        # Используем логгер из экземпляра класса
        logger = self.logger

        try:
            self.jira.add_issues_to_epic(epic_key, [issue_key])
            logger.debug(f"Задача {issue_key} привязана к эпику {epic_key}")
            return {"success": True}
        except Exception as e:
            logger.debug(f"Ошибка привязки к эпику {epic_key}: {str(e)}")
            return {"success": False, "error": str(e)}
