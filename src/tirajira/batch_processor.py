"""
Модуль для пакетной отправки задач.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .jira_client import JiraClient
from .logger import get_logger


class BatchProcessor:
    """Процессор для пакетной отправки задач в Jira."""

    def __init__(
        self,
        jira_client: JiraClient,
        batch_size: int = 10,
        delay: float = 1,
        stop_on_error: bool = False,
        verbose: bool = False,
    ) -> None:
        self.jira_client = jira_client
        self.batch_size = batch_size
        self.delay = delay
        self.stop_on_error = stop_on_error
        self.verbose = verbose
        self.logger = get_logger()

    def _prepare_processing_params(
        self,
        batch_size: Optional[int],
        delay: Optional[float],
        stop_on_error: Optional[bool],
        verbose: Optional[bool],
    ) -> Tuple[int, float, bool, bool]:
        """Подготавливает параметры обработки."""
        actual_batch_size = batch_size if batch_size is not None else self.batch_size
        actual_delay = delay if delay is not None else self.delay
        actual_stop_on_error = (
            stop_on_error if stop_on_error is not None else self.stop_on_error
        )
        actual_verbose = verbose if verbose is not None else self.verbose

        return actual_batch_size, actual_delay, actual_stop_on_error, actual_verbose

    def _setup_loggers(self, actual_verbose: bool) -> None:
        """Настраивает логгеры."""
        self.logger.set_verbose(actual_verbose)

        # Обновляем логгер в JiraClient, если это реальный объект, а не mock
        if hasattr(self.jira_client, "logger") and self.jira_client.logger is not None:
            self.jira_client.logger.set_verbose(actual_verbose)

    def _process_single_issue(
        self,
        issue_data: Dict[Any, Any],
    ) -> Tuple[Dict[str, Any], bool]:
        """Обрабатывает одну задачу."""
        # Сохраняем оригинальные данные задачи для отчета
        original_issue_data = issue_data.copy() if isinstance(issue_data, dict) else {}

        # Извлекаем epic_key если он есть, чтобы не передавать его в Jira API
        epic_key = (
            issue_data.pop("epic_key", None) if isinstance(issue_data, dict) else None
        )

        # Запоминаем время начала обработки задачи
        processed_at = datetime.now().isoformat()

        result = self.jira_client.create_issue(issue_data)
        task_detail = {
            "status": "success" if result["success"] else "failure",
            "issue_data": original_issue_data,
            "processed_at": processed_at,
        }

        success = result["success"]

        if success:
            self.logger.success(f"Задача создана: {result['issue_key']}")
            task_detail["issue_key"] = result["issue_key"]

            # Привязка к эпику, если указано
            if epic_key:
                link_result = self.jira_client.link_to_epic(
                    result["issue_key"], epic_key
                )
                if link_result["success"]:
                    self.logger.info(
                        f"Задача {result['issue_key']} привязана к эпику {epic_key}"
                    )
                else:
                    self.logger.error(
                        f"Ошибка привязки к эпику: {link_result['error']}"
                    )
                    # Добавляем информацию об ошибке в детали задачи
                    task_detail["error_message"] = (
                        f"Ошибка привязки к эпику: {link_result['error']}"
                    )
        else:
            self.logger.error(f"Ошибка создания задачи: {result['error']}")
            task_detail["error_message"] = result["error"]

        return task_detail, success

    def process(
        self,
        issues: List[Dict[Any, Any]],
        batch_size: Optional[int] = None,
        delay: Optional[float] = None,
        stop_on_error: Optional[bool] = None,
        verbose: Optional[bool] = None,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Обрабатывает список задач пачками и возвращает количество успешно
        созданных задач и детали обработки.

        Args:
            issues: Список задач для обработки.
            batch_size: Размер пакета (если None, используется значение
                        из конструктора).
            delay: Задержка между пакетами (если None, используется значение
                   из конструктора).
            stop_on_error: Прекратить обработку при ошибке (если None,
                           используется значение из конструктора).
            verbose: Подробный режим (если None, используется значение
                     из конструктора).

        Returns:
            Кортеж из количества успешно созданных задач и списка с деталями
            обработки каждой задачи.
        """
        # Используем переданные параметры или значения по умолчанию
        actual_batch_size, actual_delay, actual_stop_on_error, actual_verbose = (
            self._prepare_processing_params(batch_size, delay, stop_on_error, verbose)
        )

        # Обновляем логгеры
        self._setup_loggers(actual_verbose)

        successful_count = 0
        processing_details = []

        for i in range(0, len(issues), actual_batch_size):
            batch = issues[i : i + actual_batch_size]
            self.logger.progress(f"Отправка пачки из {len(batch)} задач...")

            # Флаг для отслеживания ошибок в текущем пакете
            batch_error = False

            # Обрабатываем все задачи в пакете, независимо от ошибок
            batch_results = []
            for idx, issue_data in enumerate(batch):
                task_detail, success = self._process_single_issue(issue_data)

                # Добавляем порядковый номер задачи
                task_detail["id"] = i + idx

                batch_results.append((task_detail, success))

                # Проверяем наличие ошибок для режима stop_on_error
                if not success or "error_message" in task_detail:
                    batch_error = True

            # Добавляем результаты пакета в общие результаты
            for task_detail, success in batch_results:
                if success:
                    successful_count += 1
                processing_details.append(task_detail)

            # Если в пакете была ошибка и включен режим остановки, прекращаем обработку
            if batch_error and actual_stop_on_error:
                self.logger.error("Обработка прекращена из-за ошибки в пакете")
                break

            # Пауза между пакетами (только если не в verbose режиме,
            # чтобы не замедлять вывод)
            if not actual_verbose and actual_delay > 0:
                time.sleep(actual_delay)

        return successful_count, processing_details
