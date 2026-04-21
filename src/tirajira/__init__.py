"""
TiraJira - инструмент для автоматизации массового создания задач в Jira.

Модуль позволяет создавать задачи в Jira из файлов JSON, YAML, CSV или Excel.
Поддерживает привязку задач к эпикам и логирование процесса создания задач.
"""

__version__ = "1.0.0"

from .batch_processor import BatchProcessor
from .commands import BaseCommand, ExtractFailedCommand, ImportCommand, ResumeCommand

# Импортируем основные классы и функции для удобства использования
from .commands.argument_parser import ArgumentParser
from .file_loaders import create_file_loader
from .jira_client import JiraClient
from .main import create_tasks_from_file
from .task_creator import TaskCreator

__all__ = [
    "ArgumentParser",
    "BatchProcessor",
    "JiraClient",
    "TaskCreator",
    "create_file_loader",
    "create_tasks_from_file",
    "BaseCommand",
    "ImportCommand",
    "ExtractFailedCommand",
    "ResumeCommand",
]
